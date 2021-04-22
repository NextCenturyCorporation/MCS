# This file is loaded as a python dictionary.  Documentation on the format
# can be found here:
# https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
#
# The goal here is to create a logging file that will work for most while
# providing additional options to make changing the configuration relatively
# easy.
{
    "version": 1,
    # Essentially the default.  Anything that isn't defined elsewhere, will
    # take these settings
    "root": {
        "level": "WARN",
        "handlers": ["console", "debug-file"],
        "propagate": False
    },
    "loggers": {
        # Sets all machine_common_sense loggers to these settings and
        # logs them into the listed handlers
        "machine_common_sense": {
            "level": "DEBUG",
            "handlers": ["console", "debug-file"],
            "propagate": False
        }
        # Sample of how to change the level at a more detailed level:
        # ,
        # "machine_common_sense.controller": {
        #    "level": "TRACE",
        #    "handlers": ["console", "debug-file"],
        #    "propagate": False
        # }
    },
    # Handlers take log messages and put them somewhere (console, files,
    # sockets, syslog, smtp, http)
    # See https://docs.python.org/3/library/logging.handlers.html for
    # all the different built in handlers
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "brief",
            "level": "DEBUG",
            "stream": "ext://sys.stdout"
        },
        # The file handlers have a nice feature to rotate log files so you
        # don't use up all your disk space (maxBytes and backupCount).
        "debug-file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "precise",
            "filename": "logs/mcs.debug.log",
            "maxBytes": 10240000,
            "backupCount": 3
        },
        # This is mostly here for a sample.  We don't seem to have enough
        # differentiation between debug and info yet to make this useful
        "info-file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "precise",
            "filename": "logs/mcs.info.log",
            "maxBytes": 10240000,
            "backupCount": 3
        }
    },
    # Formatters just specify the format of the log message.  Sometimes its
    # useful to have a lot of detail.  Sometimes it more annoying than useful.
    # Simply change which formatter you want in the handlers section.False
    "formatters": {
        "brief": {
            "format": "%(message)s"
        },
        "precise": {
            "format": "%(asctime)s <%(levelname)s>: %(message)s"
        },
        "full": {
            "format": "[%(name)s] %(asctime)s <%(levelname)s>: %(message)s"
        }
    }
}
