from logging import getLogger, INFO, StreamHandler, Formatter, Filter, WARNING, ERROR
from logging.handlers import TimedRotatingFileHandler

# Initialize logger
logger = getLogger(__name__)
logger.setLevel(INFO)

# File handler for all logs
file_handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1)
file_handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(INFO)
logger.addHandler(file_handler)

# Stream handler for INFO logs
info_stream_handler = StreamHandler()
info_stream_handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
info_stream_handler.setLevel(INFO)
info_stream_handler.addFilter(Filter('INFO'))
logger.addHandler(info_stream_handler)

# Stream handler for WARN logs
warn_stream_handler = StreamHandler()
warn_stream_handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
warn_stream_handler.setLevel(WARNING)
warn_stream_handler.addFilter(Filter('WARNING'))
logger.addHandler(warn_stream_handler)

# Stream handler for ERROR logs
error_stream_handler = StreamHandler()
error_stream_handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_stream_handler.setLevel(ERROR)
error_stream_handler.addFilter(Filter('ERROR'))
logger.addHandler(error_stream_handler)