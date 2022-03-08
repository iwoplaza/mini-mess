class ClientCLI:
    def __init__(self, prefix='!', raw_text_handler=None):
        self.__commands = [
            (('help', '?'), 'Prints all commands', lambda: self.__print_help())
        ]
        self.__prefix = prefix
        self.__raw_text_handler = raw_text_handler

    def __print_help(self):
        print('HELP')
        for (names, description, _) in self.__commands:
            print(f"{names} - {description}")

    def __find_command(self, name):
        for cmd in self.__commands:
            (names, _, __) = cmd
            if name in names:
                return cmd

    def register_command(self, names, action, description=''):
        self.__commands.append((names, description, action))

    def handle_cmd(self, raw):
        if raw.startswith(self.__prefix):
            # Command
            cmd_name = (raw[1:]).strip()

            cmd = self.__find_command(cmd_name)
            if cmd is not None:
                (_, __, action) = cmd
                action()
            else:
                raise KeyError(f'Tried to perform unknown command: "{cmd_name}"')
        else:
            # Raw text
            if self.__raw_text_handler is not None:
                self.__raw_text_handler(raw)
