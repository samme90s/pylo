# logger.py (module)
# Wrapper for the standard Python implementation of logging.
# It acts a singleton passed around to avoid duplicate loggers.
import logging
import inspect
import os

# Define a single base format common to all handlers.
BASE_FORMAT = "%(levelname)s (%(asctime)s) [name: %(name)s func: %(funcName)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Get the log level
LOG_LEVEL = getattr(
        logging,
        os.getenv("LOG_LEVEL", "DEBUG").upper(),
        logging.DEBUG
        )
# Define the log directory and file path
LOG_FILE = os.getenv(
        key="LOG_FILE",
        default="./.logs/combined.log"
        )
# Ensure log directory exists
try:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
except Exception as exc:
    raise SystemExit(f"Failed to create log directory: {exc}")


# Define a custom formatter with ANSI color codes
class CustomFormatter(logging.Formatter):
    # ANSI escape codes for colors
    grey = "\x1b[38;21m"
    blue = "\x1b[34;01m"
    yellow = "\x1b[33;01m"
    red = "\x1b[31;01m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    # Map each logging level to a color-coded format
    FORMATS = {
        logging.DEBUG: grey + BASE_FORMAT + reset,
        logging.INFO: blue + BASE_FORMAT + reset,
        logging.WARNING: yellow + BASE_FORMAT + reset,
        logging.ERROR: red + BASE_FORMAT + reset,
        logging.CRITICAL: bold_red + BASE_FORMAT + reset
        }

    def format(self, record):
        # Retrieve the format corresponding to the log record's level
        log_fmt = self.FORMATS.get(record.levelno, BASE_FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt=DATE_FORMAT)
        return formatter.format(record)


def get_logger(name: str = "") -> logging.Logger:
    '''
    Function to create or get a logger with the specified name.
    Defaults to using the caller's filename as the logger name.
    '''
    if not name:
        frame = inspect.currentframe()
        # Ensure that both the current frame and the caller's frame exist
        if frame is not None and frame.f_back is not None:
            caller_file = inspect.getfile(frame.f_back)     # Get caller's file path
            name = os.path.basename(caller_file)            # Extract just the filename
        else:
            # Fallback logger name if frame info is unavailable
            name = __name__

    # MAIN LOGGER
    # #############
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # CONSOLE
    # #############
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(CustomFormatter())

    # FILE
    # #############
    # Setting the encoding to UTF-8 here to prevent exceptions upon
    # handling characters such as emojis that are larger than 16-bit
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(BASE_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(formatter)

    # ATTACH OTHER
    # #############
    # Avoid adding duplicate FileHandlers
    # Add handlers if they are not already present
    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        logger.addHandler(console_handler)
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        logger.addHandler(file_handler)

    return logger
