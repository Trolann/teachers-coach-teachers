import logging
from logging import getLogger, INFO, StreamHandler, Formatter, Filter, WARNING, ERROR
from logging.handlers import TimedRotatingFileHandler


class LogColors:
    GREY = "\x1b[38;21m"
    YELLOW = "\x1b[38;5;226m"
    RED = "\x1b[38;5;196m"
    RESET = "\x1b[0m"


class ColorFormatter(Formatter):
    """Formatter that adds colors to log level only"""

    def format(self, record):
        # Save original levelname
        levelname = record.levelname

        # Add color to level name only
        if record.levelno == INFO:
            color = LogColors.GREY
        elif record.levelno == WARNING:
            color = LogColors.YELLOW
        elif record.levelno == ERROR:
            color = LogColors.RED
        else:
            color = LogColors.GREY

        record.levelname = f"{color}{levelname}{LogColors.RESET}"

        # Format the message
        formatted_message = super().format(record)

        # Restore original levelname
        record.levelname = levelname

        return formatted_message


class WerkzeugFormatter(ColorFormatter):
    """Special formatter for Werkzeug/Flask logs"""

    def format(self, record):
        # Extract the actual message without the IP and timestamp
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            parts = record.msg.split('] ')
            if len(parts) > 1:
                record.msg = parts[-1].strip()

        return super().format(record)


def setup_logger():
    """Setup the root logger with proper formatting and handlers"""
    # Initialize root logger
    root_logger = getLogger()
    root_logger.setLevel(INFO)

    # Remove any existing handlers
    root_logger.handlers = []

    # Declare log format once
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # File handler for all logs
    file_handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1)
    file_handler.setFormatter(Formatter(log_format))
    file_handler.setLevel(INFO)
    root_logger.addHandler(file_handler)

    # Console handler with colors for all logs
    console_handler = StreamHandler()
    console_handler.setFormatter(ColorFormatter(log_format))
    console_handler.setLevel(INFO)
    root_logger.addHandler(console_handler)

    # Special handling for Werkzeug logger
    werkzeug_logger = getLogger('werkzeug')
    werkzeug_logger.setLevel(INFO)
    # Remove default handlers
    werkzeug_logger.handlers = []

    # Add custom handler for Werkzeug
    werkzeug_handler = StreamHandler()
    werkzeug_handler.setFormatter(WerkzeugFormatter(log_format))
    werkzeug_logger.addHandler(werkzeug_handler)

    # Rename werkzeug to flask.app
    werkzeug_logger.name = 'flask.app'

    return root_logger


def get_logger(name: str):
    """Get a logger instance that inherits from root logger"""
    return getLogger(name)


# Setup root logger once at module import
setup_logger()