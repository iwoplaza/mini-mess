import logging


# Setup logger
LOG = logging.getLogger('mini-mess-server')
LOG.setLevel(logging.DEBUG)

debug_ch = logging.StreamHandler()
debug_ch.setLevel(logging.DEBUG)
# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
debug_ch.setFormatter(formatter)
# Add the handlers to the logger
LOG.addHandler(debug_ch)
