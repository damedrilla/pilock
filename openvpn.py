import os
from internetCheck import isInternetUp
from threading import Thread
import time

def startConnection():
    cmd = "cd /etc/openvpn && sudo openvpn pilock-hardware.ovpn > /dev/null 2>&1"
    returned_value = os.system(cmd)
    print('openvpn::startConnection() is terminated with return code' + returned_value)


startConThread = Thread(target=startConnection)


def connectionSwitcher():
    isConnected = False
    while True:
        localMode = isInternetUp()

        if not localMode and not isConnected:
            print('Started connecting to OpenVPN server...')
            startConThread.start()
            isConnected = True
        elif isConnected and localMode:
            #This will kill the thread as well.
            os.system('sudo killall openvpn')
            isConnected = False
        else:
            time.sleep(1)