import curses
import logging
from curses import wrapper

from src.client import LOG, AbstractLogHandler, ClientCLI
from src.client.ui import DrawContext, PromptUI, MessageBoardUI


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
    stdscr.refresh()

    msg_board_ui.draw(ctx)
    prompt_ui.draw(ctx)

    log_handler = AbstractLogHandler(handle_log)
    log_handler.setLevel(logging.INFO)
    LOG.addHandler(log_handler)

    # Welcome message
    LOG.info(f"""
<> WELCOME TO MINI-MESS! <>
===========================
Type in "!help" or "!?" to get the list of available commands.
Other than that, have fun chatting <3
    """)

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
