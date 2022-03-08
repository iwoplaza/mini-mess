import curses


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
