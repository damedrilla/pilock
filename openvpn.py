import os
from internetCheck import isInternetUp
from threading import Thread
import time

connect_to_vpn = False


def startConnection():
    while True:
        if connect_to_vpn:
            time.sleep(3)
            cmd = (
                "cd /etc/openvpn && sudo openvpn pilock-hardware.ovpn > /dev/null"
            )
            returned_value = os.system(cmd)
            print(
                #yo wtf we not c++ 
                "openvpn::startConnection() is terminated with return code "
                + str(returned_value)
            )
        else:
            time.sleep(1)


startConThread = Thread(target=startConnection)
startConThread.start()


def connectionSwitcher():
    isConnected = False
    global connect_to_vpn
    while True:
        localMode = isInternetUp()

        if not localMode and not isConnected:
            print("Started connecting to OpenVPN server...")
            connect_to_vpn = True
            isConnected = True
        elif isConnected and localMode:
            # This will kill the thread as well.
            connect_to_vpn = True
            os.system("sudo killall openvpn")
            isConnected = False
        else:
            time.sleep(1)
