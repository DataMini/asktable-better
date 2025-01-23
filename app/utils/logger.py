import logging
import sys


formatter = logging.Formatter(
    "%(levelname)s: %(filename)s:%(lineno)d %(message)s",
    datefmt="%m-%d %H:%M:%S",
)


def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = (
        False  # Prevent the log messages from being duplicated in the python console
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


log = create_logger("server")


