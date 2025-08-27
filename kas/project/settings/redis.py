import os

REDIS = {
    "HOST": os.environ.get("REDIS_HOST", "redis"),
    "PORT": 6379,
    "DB": 1,
    "DEFAULT_TIMEOUT": 360,
}
RQ_QUEUES = {"default": REDIS, "high": REDIS, "low": REDIS}
RQ_EXCEPTION_HANDLERS = ["worker.exception_handler.write_exception_to_db"]
JOB_TIMEOUT = 10800  # Tre timer
