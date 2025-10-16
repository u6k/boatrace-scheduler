from apscheduler.schedulers.blocking import BlockingScheduler


def hello():
    print("hello")

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
