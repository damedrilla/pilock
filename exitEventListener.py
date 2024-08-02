from LCDcontroller import userExit
import coloredlogs, logging
from lock_state import changeLockState
logger = logging.getLogger(__name__)
logging.basicConfig(filename='pilock.log', encoding='utf-8', level=logging.DEBUG)
coloredlogs.install(level="DEBUG", logger=logger)
def exitListener():
    while True:
        uid = input('Waiting')
        changeLockState('unlock')
        logger.info("A user goes out of the laboratory.")
        userExit()
    
