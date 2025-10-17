import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'custom_format': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'custom_format',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
        },
    },

    'loggers': {
        'boatrace_scheduler': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '__main__': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },

    'root': {
        'handlers': ['console'],
        'level': 'WARN',
    },
})


L = logging.getLogger(__name__)


def hello():
    L.debug("hello")
