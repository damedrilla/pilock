from LCDcontroller import userExit
import coloredlogs, logging
from lock_state import changeLockState
import requests
from espeakEventListener import chime
import time
logger = logging.getLogger(__name__)
logging.basicConfig(filename='pilock.log', encoding='utf-8', level=logging.INFO)
coloredlogs.install(level="DEBUG", logger=logger)
def exitListener():
    while True:
        uid = input('Waiting')
        changeLockState('unlock')
        try:
            requests.post('https://www.pilocksystem.live/api/exitstudent/'+str(uid).zfill(10), timeout=2)
        except:
            pass
        chime()
        logger.info("A user goes out of the laboratory.")
        userExit()
        time.sleep(1)
    
