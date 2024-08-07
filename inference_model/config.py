import logging
import os

log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "f": {"format": "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"}
    },
    "handlers": {
        "stream": {
            "class": "logging.StreamHandler",
            "formatter": "f",
            "level": logging.INFO,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(log_directory, "classifier.log"),
            "mode": "a",
            "maxBytes": 100000,
            "backupCount": 5,
            "formatter": "f",
            "level": logging.INFO,
        },
    },
    "loggers": {
        "": {"handlers": ["stream", "file"], "level": logging.INFO, "propagate": False},
        "root": {
            "handlers": ["stream", "file"],
            "level": logging.INFO,
            "propagate": False,
        },
    },
}
