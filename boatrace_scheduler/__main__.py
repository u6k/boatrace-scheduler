import logging
import logging.config

from apscheduler.schedulers.blocking import BlockingScheduler

logging.config.fileConfig("./logging.conf")

L = logging.getLogger("boatrace_scheduler")


def hello():
    L.debug("hello")


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(
        hello,
        "interval",
        seconds=1,
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
