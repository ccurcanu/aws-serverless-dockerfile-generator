# -*- coding: utf-8 -*-

import logging

import dockerfilegenerator.generator as generator

LOGGING_FORMAT = "%(asctime)s| %(levelname)s: %(message)s"


def setup_logging():
    logger = logging.getLogger()
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    logging.basicConfig(format=LOGGING_FORMAT, level=logging.DEBUG)
    return logger


logger = setup_logging()


def lambda_handler(event, context):
    exit_code = 0
    try:
        exit_code = generator.lambda_handler()
        if exit_code == 0:
            logger.info("Lambda function successfully executed.")
    except Exception:
        logger.error("Lambda function failed:", exc_info=True)
    return exit_code
