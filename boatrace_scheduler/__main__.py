import json
import logging
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler

import boatrace_scheduler.utils as utils

L = logging.getLogger(__name__)

SCHEDULER = None


def add_crawl_race_jobs():
    L.debug("#add_crawl_race_jobs: start")

    target_date = datetime.now()
    path_calendar = Path(os.environ.get("DATA_DIR")) / f"calendar_{target_date.strftime('%Y%m%d')}.json"
    L.debug(f"reading...{path_calendar}")

    with open(path_calendar, "r") as f:
        list_calendar = json.load(f)

    for item in list_calendar:
        if item["url"][0].endswith("#info"):
            race_url = item["url"][0].replace("#info", "")
            start_datetime = datetime.strptime(f"{target_date.strftime('%Y%m%d')} {item['start_time'][0]}", "%Y%m%d %H:%M")

            for before_minutes in [30, 20, 15, 10, 5, 2]:
                crawl_datetime = start_datetime - timedelta(minutes=before_minutes)

                L.debug(f"add post_crawl_at_race job: {crawl_datetime=}, {race_url=}, {target_date=}, {before_minutes=}")
                SCHEDULER.add_job(
                    post_crawl_at_race,
                    "date",
                    run_date=crawl_datetime,
                    args=[crawl_datetime, race_url, target_date, before_minutes],
                )


def post_crawl_at_race(crawl_datetime, race_url, target_date, before_minutes):
    L.debug(f"#post_crawl_at_race: start: {crawl_datetime=}, {race_url=}, {target_date=}, {before_minutes=}")
    try:
        race_url_pattern = re.compile(r"https:\/\/www\.boatrace\.jp\/owpc\/pc\/race\/racelist\?rno=([0-9]+)&jcd=([0-9]{2})&hd=([0-9]{8})")
        race_url_re = race_url_pattern.search(race_url)
        if race_url_re:
            json_name = "race_" + race_url_re.group(3) + "_" + race_url_re.group(2) + "_" + race_url_re.group(1) + f"_before_{before_minutes}minutes.json"
        else:
            raise Exception(f"Unknown race_url: {race_url}")

        msg = f'{{"start_url":"{race_url}","AWS_S3_FEED_URL":"s3://{os.environ.get("S3_BUCKET")}/feed/racelist/{json_name}","RECACHE_RACE":"True","RECACHE_DATA":"False"}}'

        utils.post_message(msg)
        L.debug(f"{msg=}")
    except:  # noqa
        L.exception("post_crawl_at_race")


def post_crawl_at_today():
    L.debug("#post_crawl_at_today: start")
    try:
        date = datetime.now().strftime("%Y%m%d")
        msg = f'{{"start_url":"https://www.boatrace.jp/owpc/pc/race/index?hd={date}","AWS_S3_FEED_URL":"s3://{os.environ.get("S3_BUCKET")}/feed/calendar/calendar_{date}.json","RECACHE_RACE":"True","RECACHE_DATA":"False"}}'

        utils.post_message(msg)
        L.debug(f"{msg=}")
    except:  # noqa
        L.exception("post_crawl_at_today")


def post_crawl_at_yesterday():
    L.debug("#post_crawl_at_yesterday: start")
    try:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        msg = f'{{"start_url":"https://www.boatrace.jp/owpc/pc/race/index?hd={date}","AWS_S3_FEED_URL":"s3://{os.environ.get("S3_BUCKET")}/feed/calendar/calendar_{date}.json","RECACHE_RACE":"True","RECACHE_DATA":"False"}}'

        utils.post_message(msg)
        L.debug(f"{msg=}")
    except:  # noqa
        L.exception("post_crawl_at_yesterday")


if __name__ == "__main__":
    SCHEDULER = BlockingScheduler()

    # 当日クロールをスケジュール登録
    cron_crawl_at_today = json.loads(os.environ.get("CRON_CRAWL_AT_TODAY"))
    L.debug(f"{cron_crawl_at_today=}")

    SCHEDULER.add_job(
        post_crawl_at_today,
        "cron",
        **cron_crawl_at_today,
    )

    # 昨日クロールをスケジュール登録
    cron_crawl_at_yesterday = json.loads(os.environ.get("CRON_CRAWL_AT_YESTERDAY"))
    L.debug(f"{cron_crawl_at_yesterday=}")

    SCHEDULER.add_job(
        post_crawl_at_yesterday,
        "cron",
        **cron_crawl_at_yesterday,
    )

    # レース直前クロールジョブ登録ジョブをスケジュール登録
    cron_add_crawl_at_race_jobs = json.loads(os.environ.get("CRON_ADD_CRAWL_AT_RACE_JOBS"))
    L.debug(f"{cron_add_crawl_at_race_jobs=}")

    SCHEDULER.add_job(
        add_crawl_race_jobs,
        "cron",
        **cron_add_crawl_at_race_jobs,
    )

    # スケジューラーを開始
    try:
        L.info("Starting scheduler")
        SCHEDULER.start()
    except KeyboardInterrupt:
        SCHEDULER.shutdown()
        L.info("Shutting down scheduler")
