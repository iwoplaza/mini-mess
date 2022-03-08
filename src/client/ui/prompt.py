import curses

from ..client_logger import LOG
from .ctx import DrawContext


class PromptUI:
    def __init__(self, stdscr, h, w, y, x) -> None:
        self.__value = ''
        self.__stdscr = stdscr
        self.__win = curses.newwin(h, w, y, x)

        self.__cursor_x = x + 1
        self.__cursor_y = y + 1

    def __update_cursor(self):
        self.__stdscr.move(self.__cursor_y, self.__cursor_x + len(self.__value))

    def prompt_key(self):
        key = self.__stdscr.getkey()

        if key == "\n":
            v = self.__value
            self.__value = ''
            return v
        elif ord(key) == 8:
            self.__value = self.__value[:-1]
            LOG.debug(f'Pressed backspace')
            return None

        
        # if re.match('[!\w\d\s\']', key):
        LOG.debug(f'Pressed key: \"{key}\" (ord: {ord(key)})')
        self.__value += key
        
        return None

    def draw(self, ctx: DrawContext):
        self.__win.clear()
        self.__win.border()
        self.__win.addstr(0, 2, 'Logged in as ')
        self.__win.addstr('user', ctx.CYAN_ON_BLACK)

        self.__win.addstr(1, 1, self.__value)

        self.__win.refresh()

        self.__update_cursor()
