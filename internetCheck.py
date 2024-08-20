import urllib.request
import socket
import coloredlogs, logging
import time
logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)
localMode = False
internetWarningDone = False
def isInternetUp():
    global localMode
    global internetWarningDone
    try:
        host = socket.gethostbyname("1.1.1.1")
        s = socket.create_connection((host, 80), 2)
        s.close()
        cloud_status = urllib.request.urlopen("http://152.42.167.108/").getcode()
        if cloud_status == 200:
            if internetWarningDone == False or localMode == True:
                logger.info("Connected to server")
                internetWarningDone = True
            localMode = False
    except Exception:
        if localMode == False and internetWarningDone == True:
            logger.critical(
                "No Internet connection or the server is unavailable. Switching to local mode. "
            )
        elif internetWarningDone == False:
            logger.critical(
                "No Internet connection or the server is unavailable. Switching to local mode. "
            )
            internetWarningDone = True
        localMode = True

def internetCheck():
    while True:
        isInternetUp()
        time.sleep(1)