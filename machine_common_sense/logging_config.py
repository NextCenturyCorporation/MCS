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
import copy
import logging
import os
from typing import List, Union

logger = logging.getLogger(__name__)

TRACE = 5


class LoggingConfig():

    @staticmethod
    def init_logging(log_config=None,
                     log_config_file="log.config.user.py"):
        """
        Initializes logging system.  Attempts to read file first,
        which should not be checked in and each user can have their own.
        If user file doesn't exist, then there is a base config that
        should be read.
        """
        LoggingConfig._add_trace()
        init_message = ""
        if (os.path.exists(log_config_file)):
            with open(log_config_file, "r") as data:
                log_config = ast.literal_eval(data.read())
                init_message = f"Loaded logging config from {log_config_file}"
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
    def _add_trace():
        logging.addLevelName(TRACE, "TRACE")

        def trace(self, message, *args, **kws):
            if self.isEnabledFor(TRACE):
                self._log(TRACE, message, args, **kws)
        logging.Logger.trace = trace
        logging.TRACE = TRACE

    @staticmethod
    def get_default_console_config():
        return LoggingConfig.get_configurable_logging_config(
            log_level='DEBUG',
            logger_names=['machine_common_sense'],
            console=True, debug_file=False, info_file=False,
            log_file_name="mcs",
            console_format='brief'
        )

    @staticmethod
    def get_errors_only_console_config():
        return LoggingConfig.get_configurable_logging_config(
            log_level='ERROR',
            logger_names=['machine_common_sense'],
            console=True, debug_file=False, info_file=False,
            log_file_name="mcs", file_format='precise',
            console_format='brief')

    @staticmethod
    def get_no_logging_config():
        return {
            "version": 1,
            "loggers": {},
            "handlers": {}
        }

    def get_dev_logging_config():
        '''Note: This logging configuration needs the log directory to be
        created relative to the current working directory of the python
        execution.
        '''
        return LoggingConfig.get_configurable_logging_config(
            log_level='DEBUG',
            logger_names=['machine_common_sense'],
            console=True, debug_file=True, info_file=False,
            log_file_name="mcs", file_format='precise',
            console_format='brief')

    @staticmethod
    def get_configurable_logging_config(
            log_level: str = 'DEBUG',
            logger_names: Union[List[str], str] = None,
            console: bool = True,
            debug_file: bool = True,
            info_file: bool = False,
            log_file_name: str = "mcs",
            file_format: str = 'precise',
            console_format: str = 'brief',
            root_log_level: str = 'WARN'):
        """[summary]

        Args:
            log_level (str, optional): The log level for all loggers including
                root.  Can be 'ERROR', 'WARNING', 'INFO', 'DEBUG', or 'TRACE'.
                Defaults to 'DEBUG'.
            logger_names (Union[List[str], str], optional): Names of the
                loggers to create.  Each logger specifies the level for all
                packages or modules under it.
                Defaults to ['machine_common_sense'].
            console (bool, optional): Whether the console logger is on or off.
                Defaults to True.
            debug_file (bool, optional): Whether logs should be written to the
                debug log file. This requires the 'log' directory to exist.
                Defaults to True.
            info_file (bool, optional): Whether logs should be written to the
                info log file. This requires the 'log' directory to exist.
                Defaults to False.
            log_file_name (str, optional): The base name of the log file.  This
                is usually an abbreviate for the project or product.
                Defaults to "mcs".
            file_format (str, optional): Format of the log output for log
                files. Options: 'brief', 'precise', 'full'
                Defaults to 'precise'.
            console_format (str, optional): Format of the log output for
                console logging. Options: 'brief', 'precise', 'full'.
                Defaults to 'brief'.

        Returns:
            A dictionary containing a logging configuration created from the
            parameters.
        """

        if logger_names is None:
            logger_names = ['machine_common_sense']
        logger_names = logger_names if isinstance(
            logger_names, list) else [logger_names]
        handler_tags = []

        handlers = {}
        if console:
            handler_tags.append("console")
            handlers['console'] = {
                "class": "logging.StreamHandler",
                "formatter": console_format,
                "level": log_level,
                "stream": "ext://sys.stdout"
            }
        if debug_file:
            handler_tags.append("debug-file")
            handlers["debug-file"] = {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": file_format,
                "filename": f"logs/{log_file_name}.debug.log",
                "maxBytes": 10240000,
                "backupCount": 3
            }
        if info_file:
            handler_tags.append("info-file")
            handlers["info-file"] = {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": file_format,
                "filename": f"logs/{log_file_name}.debug.log",
                "maxBytes": 10240000,
                "backupCount": 3
            }

        logger_template = {
            "level": log_level,
            "handlers": handler_tags,
            "propagate": False
        }

        loggers = {}
        for name in logger_names:
            logger = copy.deepcopy(logger_template)
            loggers[name] = logger

        return {
            "version": 1,
            "root": {
                "level": root_log_level,
                "handlers": handler_tags,
                "propagate": False
            },
            "loggers": loggers,
            "handlers": handlers,
            "formatters": {
                "brief": {
                    "format": "%(message)s"
                },
                "precise": {
                    "format": "%(asctime)s <%(levelname)s>: %(message)s"
                },
                "full": {
                    "format": "[%(name)s] %(asctime)s <%(levelname)s>: "
                    "%(message)s"
                }
            }
        }


# Call init logging early with no config to ensure it is called.  Logging
# config can always be overwritten any time MCS is used.
LoggingConfig.init_logging(LoggingConfig.get_errors_only_console_config())
