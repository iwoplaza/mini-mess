import curses

from .ctx import DrawContext
from .message import MessageUI


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
