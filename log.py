import logging

def getLogger(appName):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger