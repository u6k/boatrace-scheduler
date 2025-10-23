import json
import os

from apscheduler.schedulers.blocking import BlockingScheduler

import boatrace_scheduler.jobs as jobs
import boatrace_scheduler.utils as utils

L = utils.get_logger(__name__)


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # 当日クロールをスケジュール登録
    cron_crawl_at_today = json.loads(os.environ.get("CRON_CRAWL_AT_TODAY"))
    L.debug(f"{cron_crawl_at_today=}")

    scheduler.add_job(
        jobs.post_crawl_at_today,
        "cron",
        misfire_grace_time=None,
        **cron_crawl_at_today,
    )

    # 昨日クロールをスケジュール登録
    cron_crawl_at_yesterday = json.loads(os.environ.get("CRON_CRAWL_AT_YESTERDAY"))
    L.debug(f"{cron_crawl_at_yesterday=}")

    scheduler.add_job(
        jobs.post_crawl_at_yesterday,
        "cron",
        misfire_grace_time=None,
        **cron_crawl_at_yesterday,
    )

    # レース直前クロールジョブ登録ジョブをスケジュール登録
    cron_add_crawl_at_race_jobs = json.loads(os.environ.get("CRON_ADD_CRAWL_AT_RACE_JOBS"))
    L.debug(f"{cron_add_crawl_at_race_jobs=}")

    scheduler.add_job(
        jobs.add_crawl_race_jobs,
        "cron",
        misfire_grace_time=None,
        args=[scheduler],
        **cron_add_crawl_at_race_jobs,
    )

    # スケジューラーを開始
    try:
        L.info("Starting scheduler")
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
        L.info("Shutting down scheduler")
