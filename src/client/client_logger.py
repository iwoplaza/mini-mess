import logging


# Setup logger
LOG = logging.getLogger('mini-mess')
LOG.setLevel(logging.DEBUG)
info_fh = logging.FileHandler('client_info.log')
info_fh.setLevel(logging.INFO)
debug_fh = logging.FileHandler('client_debug.log')
debug_fh.setLevel(logging.DEBUG)
error_fh = logging.FileHandler('client_error.log')
error_fh.setLevel(logging.ERROR)
# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
info_fh.setFormatter(formatter)
debug_fh.setFormatter(formatter)
error_fh.setFormatter(formatter)
# Add the handlers to the logger
LOG.addHandler(info_fh)
LOG.addHandler(debug_fh)
LOG.addHandler(error_fh)


class AbstractLogHandler(logging.Handler):
    def __init__(self, reaction, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__reaction = reaction

    def emit(self, record):
        s = self.format(record)
        self.__reaction(s)