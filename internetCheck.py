import urllib.request
import socket
import coloredlogs, logging
import time

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)
internetWarningDone = False
localMode = True

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
                return False
    except Exception:
            return True


localMode = isInternetUp()
def internetCheck():
        isInternetUp()
