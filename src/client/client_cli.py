from .client_logger import LOG


class ClientCLI:
    def __init__(self, prefix='!', raw_text_handler=None):
        self.__commands = [
            (('help', '?'), 'Shows this list', lambda: self.__print_help())
        ]
        self.__prefix = prefix
        self.__raw_text_handler = raw_text_handler

    def __print_help(self):
        msg = 'Here\'s a list of available commands: \n'
        
        for (names, description, _) in self.__commands:
            msg += f"{names} - {description}\n"
        
        LOG.info(msg)

    def __find_command(self, name):
        for cmd in self.__commands:
            (names, _, __) = cmd
            if name in names:
                return cmd

    def register_command(self, names, action, description=''):
        self.__commands.append((names, description, action))

    def handle_cmd(self, raw: str):
        if raw.startswith(self.__prefix):
            # Command
            raw = raw[len(self.__prefix):] # Removing the prefix
            delimiter_idx = raw.find(' ')
            cmd_name = (raw[:delimiter_idx]).strip()
            
            rest = None
            if delimiter_idx != -1:
                rest = raw[(delimiter_idx+1):]

            cmd = self.__find_command(cmd_name)
            if cmd is not None:
                (_, __, action) = cmd
                action(cmd_name, rest)
            else:
                raise KeyError(f'Tried to perform unknown command: "{cmd_name}"')
        else:
            # Raw text
            if self.__raw_text_handler is not None:
                self.__raw_text_handler(raw)
