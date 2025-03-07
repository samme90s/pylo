# logger.py (module)
# Wrapper for the standard Python implementation of logging.
# It acts a singleton (if same name is present) passed around
# to avoid duplicate loggers.
import logging
import inspect
import os
import copy

# Define a single base format common to all handlers.
BASE_FORMAT = (
    "%(levelname)s (%(asctime)s) [name: %(name)s func: %(funcName)s] %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def try_create_dir(path: str):
    # Extract the directory portion of the path.
    directory = os.path.dirname(path)
    # Only attempt to create the directory if it isn't an empty string.
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as exc:
            raise SystemExit(f"Failed to create directory: {exc}")


# Define a custom formatter with ANSI color codes
class ASCIIFormatter(logging.Formatter):
    # Maximum length for the message portion of the log
    max_message_length = 100

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
        logging.CRITICAL: bold_red + BASE_FORMAT + reset,
    }

    def format(self, record):
        # Make a shallow copy of the record so that the original is not modified.
        record_copy = copy.copy(record)

        # Retrieve the original message using the record's formatting logic.
        original_message = record_copy.getMessage()

        # Truncate the message if it is longer than max_message_length
        if len(original_message) > self.max_message_length:
            # Store the truncated version back into the record.
            # Note: We override msg and args so that record.getMessage() returns the truncated version.
            record_copy.msg = original_message[: self.max_message_length] + "..."
            record_copy.args = None

        # Retrieve the format corresponding to the log record's level
        log_fmt = self.FORMATS.get(record_copy.levelno, BASE_FORMAT)
        formatter = logging.Formatter(fmt=log_fmt, datefmt=DATE_FORMAT)
        return formatter.format(record=record_copy)


def get_logger(name: str = "") -> logging.Logger:
    """
    Function to create or get a logger with the specified name.
    Defaults to using the caller's filename as the logger name.
    """
    if not name:
        frame = inspect.currentframe()
        # Ensure that both the current frame and the caller's frame exist
        if frame is not None and frame.f_back is not None:
            caller_file = inspect.getfile(frame.f_back)  # Get caller's file path
            name = os.path.basename(caller_file)  # Extract just the filename
        else:
            # Fallback logger name if frame info is unavailable
            name = __name__

    # MAIN LOGGER
    # #############
    logger = logging.getLogger(name)

    # If no handlers are found then we assume that the logger has already been
    # setup... skipping this process.
    if not logger.handlers:
        # Get and set the log level.
        LOG_LEVEL = getattr(
            logging, os.getenv(key="LOG_LEVEL", default="DEBUG").upper(), logging.DEBUG
        )
        logger.setLevel(level=LOG_LEVEL)

        # Define the log directory and file path and try create the directory
        # for it.
        LOG_FILE = os.getenv(key="LOG_FILE", default="combined.log")
        try_create_dir(path=LOG_FILE)

        # CONSOLE
        # #############
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level=LOG_LEVEL)
        console_handler.setFormatter(fmt=ASCIIFormatter())
        logger.addHandler(console_handler)

        # FILE
        # #############
        # Setting the encoding to UTF-8 here to prevent exceptions upon
        # handling characters such as emojis that are larger than 16-bit
        file_handler = logging.FileHandler(filename=LOG_FILE, encoding="utf-8")
        file_handler.setLevel(level=LOG_LEVEL)
        file_handler.setFormatter(
            fmt=logging.Formatter(fmt=BASE_FORMAT, datefmt=DATE_FORMAT)
        )
        logger.addHandler(file_handler)

    return logger
