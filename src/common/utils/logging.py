import os
import time
import logging


def setupLogger(logging_level=logging.ERROR):
    if not os.path.exists("log"):
        os.makedirs("log")
    time.strftime("pyibapi.%Y%m%d_%H%M%S.log")
    recfmt = '(%(threadName)s) [%(asctime)s.%(msecs)03d] %(levelname)s %(filename)s:%(lineno)d %(message)s'
    timefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(
        filename=time.strftime("log/%Y%m%d_%H%M%S.log"),
        filemode="w",
        level=logging.INFO,
        format=recfmt,
        datefmt=timefmt
    )
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging_level)
    logger.addHandler(console)