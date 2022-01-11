# This is additional documentation for logging configuration dictionaries.
# Documentation on the format can be found here:
# https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
#
#
# Basic structure of logging.
#   Code should get and use a logger determined by the class name:
#     logger = logging.getLogger(__name__)
#   Loggers are configured here to pass log data zero or more handlers
#     Loggers have a level which filters out any logs below that level
#   Handlers determine where to send the data (console, files, sockets)
#     Handlers have a level which filters out any logs below that level
#     Handlers can reference a formatter
#   Formatters determine the format of the log message
#   Note: For a message to be logged, its level must be equal to or above
#     both the logger's level and the handler's level
#
# "root" is Essentially the default.  Anything that isn't defined elsewhere,
# will take these settings
#
# "loggers" Sets all machine_common_sense loggers to these settings and
# logs them into the listed handlers
#
# "handlers" take log messages and put them somewhere (console, files,
# sockets, syslog, smtp, http)
# See https://docs.python.org/3/library/logging.handlers.html for
# all the different built in handlers
#
# The file handlers have a nice feature to rotate log files so you
# don't use up all your disk space (maxBytes and backupCount).
#
# creating separate file handlers can be useful, but we don't seem to have
# enough differentiation between debug and info yet to make this useful
#
# Formatters just specify the format of the log message.  Sometimes its
# useful to have a lot of detail.  Sometimes it more annoying than useful.
# Simply change which formatter you want in the handlers
# section.

import ast
import logging
import os

logger = logging.getLogger(__name__)


class LoggingConfig():

    default_console_config = {
        "version": 1,
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False
        },
        "loggers": {
            "machine_common_sense": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "brief",
                "level": "DEBUG",
                "stream": "ext://sys.stdout"
            }
        },
        "formatters": {
            "brief": {
                "format": "%(message)s"
            }
        }
    }

    @staticmethod
    def init_logging(log_config=None,
                     log_config_file="log.config.user.py"):
        """
        Initializes logging system.  Attempts to read file first,
        which should not be checked in and each user can have their own.
        If user file doesn't exist, then there is a base config that
        should be read.
        """
        init_message = ""
        if (os.path.exists(log_config_file)):
            with open(log_config_file, "r") as data:
                log_config = ast.literal_eval(data.read())
                init_message = "Loaded logging config from " + log_config_file
        elif log_config is not None:
            init_message = "Loaded provided logging config dictionary"
        if (log_config is None):
            log_config = LoggingConfig.get_default_console_config()
            init_message = "Loaded default logging config"

        if (not os.path.exists("logs")):
            os.mkdir("logs")
        logging.config.dictConfig(log_config)
        logger.info(init_message)

    @staticmethod
    def get_default_console_config():
        return LoggingConfig.default_console_config

    @staticmethod
    def get_errors_only_console_config():
        return {
            "version": 1,
            "root": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": False
            },
            "loggers": {
                "machine_common_sense": {
                    "level": "ERROR",
                    "handlers": ["console"],
                    "propagate": False
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "brief",
                    "level": "DEBUG",
                    "stream": "ext://sys.stdout"
                }
            },
            "formatters": {
                "brief": {
                    "format": "%(message)s"
                }
            }
        }

    @staticmethod
    def get_dev_logging_config():
        '''Note: This logging configuration needs the log directory to be
        created relative to the current working directory of the python
        execution.
        '''
        return {
            "version": 1,
            "root": {
                "level": "DEBUG",
                "handlers": ["console", "debug-file"],
                "propagate": False
            },
            "loggers": {
                "machine_common_sense": {
                    "level": "DEBUG",
                    "handlers": ["console", "debug-file"],
                    "propagate": False
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "brief",
                    "level": "DEBUG",
                    "stream": "ext://sys.stdout"
                },
                "debug-file": {
                    "level": "DEBUG",
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "precise",
                    "filename": "logs/mcs.debug.log",
                    "maxBytes": 10240000,
                    "backupCount": 3
                },

                "info-file": {
                    "level": "INFO",
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "precise",
                    "filename": "logs/mcs.info.log",
                    "maxBytes": 10240000,
                    "backupCount": 3
                }
            },
            "formatters": {
                "brief": {
                    "format": "%(message)s"
                },
                "precise": {
                    "format": "%(asctime)s <%(levelname)s>: %(message)s"
                },
                "full": {
                    "format": "[%(name)s] %(asctime)s <%(levelname)s>: " +
                    "%(message)s"
                }
            }
        }
