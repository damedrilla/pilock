import os
from threading import Thread
import time
import urllib.request
import time

connect_to_vpn = False

def isInternetUp():
    try:    
        cloud_status = urllib.request.urlopen("http://152.42.167.108/", timeout=2).getcode()
        if cloud_status == 200:
            return False
    except Exception:
            return True

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

startConThread = Thread(target=startConnection)
switcher_thread = Thread(target=connectionSwitcher)
startConThread.start()
switcher_thread.start()