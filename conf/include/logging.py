# -*- coding: utf-8 -*-
__author__ = 'Nikolay Mamashin (mamashin@gmail.com)'

from loguru import logger
from conf.settings import LOGS_ROOT, DEBUG


if not DEBUG:
    # Remove the default handler in production
    logger.remove()

logger.add(f"{LOGS_ROOT}/debug.log", filter=lambda record: record["level"].name == "DEBUG")
logger.add(f"{LOGS_ROOT}/info.log", filter=lambda record: record["level"].name == "INFO")
logger.add(f"{LOGS_ROOT}/error.log", filter=lambda record: record["level"].name == "ERROR")
logger.add(f"{LOGS_ROOT}/warning.log", filter=lambda record: record["level"].name == "WARNING")
