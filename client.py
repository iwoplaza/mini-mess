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
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_WHITE)
        self.BLUE_ON_BLACK = curses.color_pair(1)
        self.CYAN_ON_BLACK = curses.color_pair(2)
        self.BLACK_ON_YELLOW = curses.color_pair(3)
        self.BLACK_ON_WHITE = curses.color_pair(4)
        self.BLUE_ON_WHITE = curses.color_pair(5)


class MessageUI:
    def __init__(self, win, y: int, msg: str, sender: str = None) -> None:
        self.__win = win
        self.__x = 2
        self.__y = y

        self.__width = min(curses.COLS - 5, 70)
        # Splitting the msg into lines
        self.__lines = msg.split('\n')
        self.__lines = map(lambda l: textwrap.wrap(l, width=self.__width), self.__lines)
        self.__lines = [line for lines in self.__lines for line in lines]
        self.height = 3 + len(self.__lines)

        self.__sender_header = f'{sender}:' if sender is not None else ''
        self.__max_line_len = max(
            max(map(lambda l: len(l), self.__lines)),
            len(self.__sender_header)
        )

    def scroll(self, offset: int):
        self.__y -= offset
    
    def is_out_of_bounds(self):
        return self.__y < 0

    def draw(self, ctx: DrawContext):
        theme = ctx.BLACK_ON_WHITE if self.__sender_header else ctx.BLACK_ON_YELLOW

        self.__win.addstr(self.__y, self.__x, chr(175))
        self.__win.addstr(' ' * (self.__max_line_len + 2), theme)

        if self.__sender_header:
            self.__win.addstr(self.__y, self.__x + 2, self.__sender_header, ctx.BLUE_ON_WHITE)

        y_offset = 1
        for line in self.__lines:
            self.__win.addstr(self.__y + y_offset, self.__x + 1, ' ', theme) # Left-padding
            self.__win.addstr(line, theme)
            self.__win.addstr(' ' * (self.__max_line_len - len(line) + 1), theme) # Right-padding
            y_offset += 1

        self.__win.addstr(self.__y + y_offset, self.__x + 1, ' ' * (self.__max_line_len + 2), theme)


class MessageBoardUI:
    def __init__(self, stdscr, h, w, y, x) -> None:
        self.__stdscr = stdscr
        self.__win = curses.newwin(h, w, y, x)
        self.__h = h
        self.__w = w
        self.__y = y
        self.__x = x
        self.__messages = []

    def scroll_and_purge(self, offset: int):
        for msg_ui in self.__messages:
            msg_ui.scroll(offset)

        self.__messages = list(filter(lambda m: not m.is_out_of_bounds(), self.__messages))

    def append_log_msg(self, msg: str, sender: str = None):
        msg_ui = MessageUI(self.__win, self.__h, msg, sender)
        self.__messages.append(msg_ui)

        self.scroll_and_purge(msg_ui.height)

    def draw(self, ctx: DrawContext):
        self.__win.clear()

        for msg_ui in self.__messages:
            msg_ui.draw(ctx)

        self.__win.refresh()


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
    PROMPT_WINDOW_HEIGHT = 3

    ctx = DrawContext()
    prompt_ui = PromptUI(stdscr, PROMPT_WINDOW_HEIGHT, curses.COLS, curses.LINES - PROMPT_WINDOW_HEIGHT, 0)
    msg_board_ui = MessageBoardUI(stdscr, curses.LINES - PROMPT_WINDOW_HEIGHT, curses.COLS, 0, 0)

    def handle_raw_text(text: str):
        msg_board_ui.append_log_msg(text, sender='user1')
        msg_board_ui.draw(ctx)

    cli = ClientCLI(raw_text_handler=handle_raw_text)
    running = True

    def cmd_quit():
        nonlocal running
        running = False

    def handle_log(log: str):
        msg_board_ui.append_log_msg(log)
        msg_board_ui.draw(ctx)

    cli.register_command(('quit', 'q'), cmd_quit, 'Quits this application.')

    stdscr.clear()
    prompt_ui.draw_bg(ctx)
    stdscr.refresh()

    msg_board_ui.draw(ctx)
    prompt_ui.draw(ctx)

    log_handler = AbstractLogHandler(handle_log)
    log_handler.setLevel(logging.INFO)
    LOG.addHandler(log_handler)

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
