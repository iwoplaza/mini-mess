import re
import curses
import logging
import textwrap
from curses import wrapper
from curses.textpad import rectangle

from src.client import LOG, AbstractLogHandler, ClientCLI


class DrawContext:
    def __init__(self) -> None:
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.BLUE_ON_BLACK = curses.color_pair(1)
        self.CYAN_ON_BLACK = curses.color_pair(2)
        self.WHITE_ON_BLUE = curses.color_pair(3)


class MessageUI:
    def __init__(self, win, y: int, msg: str, sender: str = None) -> None:
        self.__win = win
        self.__y = y

        self.__width = curses.COLS - 4
        # Splitting the msg into lines
        self.__lines = textwrap.wrap(msg, width=self.__width-2)
        self.height = 3 + len(self.__lines)

    def scroll(self, offset: int):
        self.__y -= offset
    
    def is_out_of_bounds(self):
        return self.__y < 0

    def draw(self, ctx: DrawContext):
        rectangle(self.__win, self.__y, 2, 5, curses.COLS - 4)


class MessageBoardUI:
    def __init__(self, stdscr, h, w, y, x) -> None:
        log_handler = AbstractLogHandler(lambda s: self.append_log_msg(s))
        LOG.addHandler(log_handler)

        self.__stdscr = stdscr
        self.__win = curses.newwin(h, w, y, x)
        self.__h = h
        self.__w = w
        self.__y = y
        self.__x = x
        self.__messages = []

    def scroll_and_purge(self, offset: int):
        pass

    def append_log_msg(self, msg: str, sender: str = None):
        msg_ui = MessageUI(self.__win, self.__h, msg, sender)
        self.__messages.append(msg_ui)



        self.scroll_and_purge()


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

    def draw_bg(self, ctx: DrawContext):
        pass

    def draw(self, ctx: DrawContext):
        self.__win.clear()
        self.__win.border()
        self.__win.addstr(0, 2, 'Logged in as ')
        self.__win.addstr('user', ctx.CYAN_ON_BLACK)

        self.__win.addstr(1, 1, self.__value)

        self.__win.refresh()

        self.__update_cursor()


def main(stdscr):
    PROMPT_WINDOW_HEIGHT = 4

    ctx = DrawContext()
    prompt_ui = PromptUI(stdscr, 3, curses.COLS, curses.LINES - PROMPT_WINDOW_HEIGHT, 0)

    msg_win = curses.newwin(curses.LINES - PROMPT_WINDOW_HEIGHT, curses.COLS, 0, 0)

    cli = ClientCLI()
    running = True

    def cmd_quit():
        nonlocal running
        running = False

    cli.register_command(('quit', 'q'), cmd_quit)

    stdscr.clear()
    prompt_ui.draw_bg(ctx)
    stdscr.refresh()

    msg_win.clear()
    msg_win.addstr('(User1): ')
    msg_win.refresh()

    prompt_ui.draw(ctx)

    while running:
        try:
            raw = prompt_ui.prompt_key()

            if raw is not None:
                cli.handle_cmd(raw)
            
            prompt_ui.draw(ctx)
        except KeyError as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    wrapper(main)
