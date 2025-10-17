import logging.config
import os

import pika

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


def post_message(msg):
    mq_conn = pika.BlockingConnection(pika.URLParameters(os.environ.get("MQ_URL")))
    try:
        mq_channel = mq_conn.channel()
        mq_channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MQ_QUEUE"),
            body=msg.encode("utf-8"),
        )
    finally:
        mq_conn.close()
