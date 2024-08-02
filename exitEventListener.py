import coloredlogs, logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='pilock.log', encoding='utf-8')
coloredlogs.install(level="DEBUG", logger=logger)
logging.basicConfig(filename='pilock.log', encoding='utf-8')
def exitListener():
    while True:
        uid = input('Waiting')
        logger.info("A user goes out of the laboratory.")
    
    