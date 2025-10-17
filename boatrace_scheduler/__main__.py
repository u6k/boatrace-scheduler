import json
import logging
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler

import boatrace_scheduler.utils as utils

L = logging.getLogger(__name__)


def post_crawl_at_today():
    try:
        date = datetime.now().strftime("%Y%m%d")
        msg = f'{{"start_url":"https://www.boatrace.jp/owpc/pc/race/index?hd={date}","AWS_S3_FEED_URL":"s3://{os.environ.get("S3_BUCKET")}/feed/calendar/calendar_{date}.json","RECACHE_RACE":"True","RECACHE_DATA":"False"}}'

        utils.post_message(msg)
        L.debug(f"post_crawl_at_today: {msg=}")
    except:  # noqa
        L.exception("post_crawl_at_today")


def post_crawl_at_yesterday():
    try:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        msg = f'{{"start_url":"https://www.boatrace.jp/owpc/pc/race/index?hd={date}","AWS_S3_FEED_URL":"s3://{os.environ.get("S3_BUCKET")}/feed/calendar/calendar_{date}.json","RECACHE_RACE":"True","RECACHE_DATA":"False"}}'

        utils.post_message(msg)
        L.debug(f"post_crawl_at_yesterday: {msg=}")
    except:  # noqa
        L.exception("post_crawl_at_yesterday")


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # 当日クロールをスケジュール登録
    cron_crawl_at_today = json.loads(os.environ.get("CRON_CRAWL_AT_TODAY"))
    L.debug(f"{cron_crawl_at_today=}")

    scheduler.add_job(
        post_crawl_at_today,
        "cron",
        **cron_crawl_at_today,
    )

    # 昨日クロールをスケジュール登録
    cron_crawl_at_yesterday = json.loads(os.environ.get("CRON_CRAWL_AT_YESTERDAY"))
    L.debug(f"{cron_crawl_at_yesterday=}")

    scheduler.add_job(
        post_crawl_at_yesterday,
        "cron",
        **cron_crawl_at_yesterday,
    )

    # スケジューラーを開始
    try:
        L.info("Starting scheduler")
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
        L.info("Shutting down scheduler")
