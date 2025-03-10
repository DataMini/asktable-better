import time
from app import log


def sleep_test() -> str:
    time.sleep(2)
    log.info("Sleep test done")
    return "ok"