import io
import json
import logging
import logging.config
import os

import boto3
import pika
from botocore.exceptions import ClientError

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


def get_logger(logger_name):
    return logging.getLogger(logger_name)


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


class S3Client:
    def __init__(self):
        self.s3_endpoint = os.environ.get("AWS_ENDPOINT_URL")
        self.s3_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self.s3_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.s3_bucket = os.environ.get("AWS_S3_BUCKET")

        self.s3_client = boto3.resource("s3", endpoint_url=self.s3_endpoint, aws_access_key_id=self.s3_access_key, aws_secret_access_key=self.s3_secret_key)

        self.s3_bucket_obj = self.s3_client.Bucket(self.s3_bucket)
        if not self.s3_bucket_obj.creation_date:
            self.s3_bucket_obj.create()

    def get_json(self, key):
        data_bytes = self.get_bytes(key)

        if data_bytes is not None:
            with io.BytesIO(data_bytes) as b:
                data = json.load(b)
        else:
            data = None

        return data

    def get_bytes(self, key):
        s3_obj = self.s3_bucket_obj.Object(key)

        try:
            data_bytes = s3_obj.get()["Body"].read()
        except ClientError as err:
            if err.response["Error"]["Code"] == "404" or err.response["Error"]["Code"] == "NoSuchKey":
                data_bytes = None
            else:
                raise err

        return data_bytes

    def put_json(self, key, data):
        with io.BytesIO() as b:
            json.dump(data, b)
            self.s3_bucket_obj.Object(key).put(Body=b.getvalue())

    def put_bytes(self, key, data_bytes):
        self.s3_bucket_obj.Object(key).put(Body=data_bytes)
