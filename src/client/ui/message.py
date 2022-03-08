import curses
import textwrap

from .ctx import DrawContext


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

