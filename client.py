import curses
import logging
from curses import wrapper

from src.client import LOG, AbstractLogHandler, ClientCLI, \
                       ClientConnection, ClientMode
from src.client.ui import DrawContext, PromptUI, MessageBoardUI


class App:
    def __init__(self, stdscr) -> None:
        # UI
        PROMPT_WINDOW_HEIGHT = 3
        self.__stdscr = stdscr
        self.__ctx = DrawContext()
        self.__prompt_ui = PromptUI(stdscr, PROMPT_WINDOW_HEIGHT, curses.COLS, curses.LINES - PROMPT_WINDOW_HEIGHT, 0)
        self.__msg_board_ui = MessageBoardUI(stdscr, curses.LINES - PROMPT_WINDOW_HEIGHT, curses.COLS, 0, 0)

        # Functionality
        self.__cli = ClientCLI(raw_text_handler=self.__handle_raw_text)
        self.__running = True
        self.__client_connection = ClientConnection(on_message=self.__handle_message)

        # Commands
        def cmd_quit():
            nonlocal self
            self.__running = False

        self.__cli.register_command(('quit', 'q'), cmd_quit, 'Quits this application.')

    def __handle_message(self, text: str, sender: str):
        self.__msg_board_ui.append_log_msg(text, sender=sender)
        self.__msg_board_ui.draw(self.__ctx)

    def __handle_log(self, log: str):
        self.__handle_message(log, sender=None)

    def __handle_raw_text(self, text: str):
        mode = self.__client_connection.get_mode()
        if mode == ClientMode.CONNECTING:
            return
        elif mode == ClientMode.SIGNING_IN:
            try:
                self.__client_connection.sign_in(text)
            except RuntimeError as e:
                LOG.info(f'Failed to sign-in. Reason: {e}')
                return

            LOG.info(f'Logged in as "{text}". Type in "!help" or "!?" to get the list of available commands.\n' +
                     'Other than that, have fun chatting <3')

            self.__prompt_ui.set_header_label([('Logged in as ', self.__ctx.WHITE_ON_BLACK), (self.__client_connection.get_username(), self.__ctx.CYAN_ON_BLACK)])
            self.__prompt_ui.draw(self.__ctx)
        elif mode == ClientMode.CHAT:
            self.__client_connection.send_message(text)
    
    def run(self):
        # Running connecting handling in the background.
        self.__client_connection.run()

        self.__stdscr.clear()
        self.__stdscr.refresh()

        self.__msg_board_ui.draw(self.__ctx)
        self.__prompt_ui.draw(self.__ctx)

        log_handler = AbstractLogHandler(self.__handle_log)
        log_handler.setLevel(logging.INFO)
        LOG.addHandler(log_handler)

        while self.__running:
            try:
                raw = self.__prompt_ui.prompt_key()

                if raw is not None:
                    self.__cli.handle_cmd(raw)
                
                self.__prompt_ui.draw(self.__ctx)
            except KeyError as e:
                print(f'Error: {e}')

def main(stdscr):
    app = App(stdscr)
    app.run()


if __name__ == '__main__':
    wrapper(main)
