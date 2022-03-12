import curses
import logging
from curses import wrapper

from src.client import LOG, AbstractLogHandler, ClientCLI, \
                       ClientConnection, ClientMode
from src.client.ui import DrawContext, PromptUI, MessageBoardUI


mode = ClientMode.SIGNING_IN

def main(stdscr):
    PROMPT_WINDOW_HEIGHT = 3

    ctx = DrawContext()
    prompt_ui = PromptUI(stdscr, PROMPT_WINDOW_HEIGHT, curses.COLS, curses.LINES - PROMPT_WINDOW_HEIGHT, 0)
    msg_board_ui = MessageBoardUI(stdscr, curses.LINES - PROMPT_WINDOW_HEIGHT, curses.COLS, 0, 0)

    def handle_message(text: str, sender: str):
        msg_board_ui.append_log_msg(text, sender=sender)
        msg_board_ui.draw(ctx)

    client_connection = ClientConnection(on_message=handle_message)

    def handle_raw_text(text: str):
        global mode

        if mode == ClientMode.SIGNING_IN:
            try:
                client_connection.sign_in(text)
            except RuntimeError as e:
                LOG.info(f'Failed to sign-in. Reason: {e}')
                return

            LOG.info(f"""Logged in as "{text}". Type in "!help" or "!?" to get the list of available commands.
Other than that, have fun chatting <3""")

            mode = ClientMode.CHAT
        elif mode == ClientMode.CHAT:
            client_connection.send_message(text)

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
Put in your username below
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
