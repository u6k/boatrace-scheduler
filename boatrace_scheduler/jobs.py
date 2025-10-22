import os
import re
from datetime import datetime, timedelta

import boatrace_scheduler.utils as utils

L = utils.get_logger(__name__)


def add_crawl_race_jobs(scheduler):
    L.debug("#add_crawl_race_jobs: start")

    s3_client = utils.S3Client()

    target_date = datetime.now()
    key_calendar = f"feed/calendar/calendar_{target_date.strftime("%Y%m%d")}.json"
    L.debug(f"reading...{key_calendar}")

    list_calendar = s3_client.get_json(key_calendar)

    for item in list_calendar:
        if item["url"][0].endswith("#info"):
            race_url = item["url"][0].replace("#info", "")
            start_datetime = datetime.strptime(f"{target_date.strftime('%Y%m%d')} {item['start_time'][0]}", "%Y%m%d %H:%M")

            for before_minutes in [30, 20, 15, 10, 5, 2]:
                crawl_datetime = start_datetime - timedelta(minutes=before_minutes)

                L.debug(f"add post_crawl_at_race job: {crawl_datetime=}, {race_url=}, {target_date=}, {before_minutes=}")
                scheduler.add_job(
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

        msg = f'{{"start_url":"{race_url}","AWS_S3_FEED_URL":"s3://{os.environ.get("AWS_S3_BUCKET")}/feed/racelist/{target_date.strftime("%Y%m%d")}/{json_name}","RECACHE_RACE":"True","RECACHE_DATA":"False"}}'

        utils.post_message(msg)
        L.debug(f"{msg=}")
    except:  # noqa
        L.exception("post_crawl_at_race")


def post_crawl_at_today():
    L.debug("#post_crawl_at_today: start")
    try:
        date = datetime.now().strftime("%Y%m%d")
        msg = f'{{"start_url":"https://www.boatrace.jp/owpc/pc/race/index?hd={date}","AWS_S3_FEED_URL":"s3://{os.environ.get("AWS_S3_BUCKET")}/feed/calendar/calendar_{date}.json","RECACHE_RACE":"True","RECACHE_DATA":"False"}}'

        utils.post_message(msg)
        L.debug(f"{msg=}")
    except:  # noqa
        L.exception("post_crawl_at_today")


def post_crawl_at_yesterday():
    L.debug("#post_crawl_at_yesterday: start")
    try:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        msg = f'{{"start_url":"https://www.boatrace.jp/owpc/pc/race/index?hd={date}","AWS_S3_FEED_URL":"s3://{os.environ.get("AWS_S3_BUCKET")}/feed/calendar/calendar_{date}.json","RECACHE_RACE":"True","RECACHE_DATA":"False"}}'

        utils.post_message(msg)
        L.debug(f"{msg=}")
    except:  # noqa
        L.exception("post_crawl_at_yesterday")
