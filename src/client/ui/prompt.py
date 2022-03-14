import curses

from ..client_logger import LOG
from .ctx import DrawContext


QUIT_KEY_CODES = [
    3, # Interrupt (Ctrl+C)
    26, # Ctrl+Z
    27, # Escape
]

IGNORE_KEY_CODES = [
    0 # Null char
]


class PromptUI:
    def __init__(self, stdscr, h, w, y, x) -> None:
        self.__value = ''
        self.__stdscr = stdscr
        self.__win = curses.newwin(h, w, y, x)

        self.__cursor_x = x + 1
        self.__cursor_y = y + 1

        self.__header_label = []

    def __update_cursor(self):
        self.__stdscr.move(self.__cursor_y, self.__cursor_x + len(self.__value))

    def prompt_key(self):
        key = self.__stdscr.getkey()

        if len(key) > 1:
            LOG.debug(f'Pressed special key: {key}')
            return None
        elif key == "\n": # Enter
            if len(self.__value) > 0:
                v = self.__value
                self.__value = ''
                return v
            return None
        elif ord(key) == 8: # Backspace
            self.__value = self.__value[:-1]
            return None
        elif ord(key) in QUIT_KEY_CODES:
            return '!q'
        elif ord(key) in IGNORE_KEY_CODES:
            return None
        
        # if re.match('[!\w\d\s\']', key):
        LOG.debug(f'Pressed key: \"{key}\" (ord: {ord(key)})')
        self.__value += key
        
        return None

    def set_header_label(self, header_label):
        self.__header_label = header_label

    def draw(self, ctx: DrawContext):
        self.__win.clear()
        self.__win.border()
        self.__win.move(0, 2)
        # self.__win.addstr(0, 2, '')
        for (text, style) in self.__header_label:
            self.__win.addstr(text, style)

        self.__win.addstr(1, 1, self.__value)

        self.__win.refresh()

        self.__update_cursor()
