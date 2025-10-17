import logging

from apscheduler.schedulers.blocking import BlockingScheduler

import boatrace_scheduler.utils as utils

L = logging.getLogger(__name__)


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(
        utils.hello,
        "interval",
        seconds=1,
    )

    try:
        L.info("Starting scheduler")
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
        L.info("Shutting down scheduler")
