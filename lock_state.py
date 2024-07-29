import RPi.GPIO as GPIO
from threading import Thread
import time
import coloredlogs, logging
from guestModeTracker import guestMode_QuestionMark

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)

# Time remaining until the door locks again
# This is the condition if the door is locked or otherwise (>0 = unlocked)
timeRemaining = 0
timerDoneWarning = True
# For lock state change detection in lockstate() method (true means door is locked)
doorIsLocked = True

guestMode = False
# There is no way (or too impractical to do) to interrupt a time.sleep() in Python so this is the workaround.
# timeRemaining decrements every loop. An iteration lasts a second
def countItDown():
    global timeRemaining
    global timerDoneWarning
    while True:
        if timeRemaining != 0:
            timerDoneWarning = False
            timeRemaining -= 1
            print(str(timeRemaining) + " seconds remaining", end="\r")
            time.sleep(1)
        else:
            if timerDoneWarning == False:
                logger.warning("No time left!")
                timerDoneWarning = True
            time.sleep(1)
            continue


# This method is the one who controls the lock state
# Uses the time remaining as condition if the lock is on or off
# Magnet lock is connected though normally closed port in the relay
def lockState():
    global guestMode
    global doorIsLocked
    # Set them pinouts for relay and the mag lock itself
    GPIO.setmode(GPIO.BCM)
    RELAY_PIN = 4
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    while True:
        if not guestMode:
            if timeRemaining == 0:
                if doorIsLocked != True:
                    doorIsLocked = True
                    # Send a signal to the relay to lock the thing
                    logger.info("State changed to locked")
                    GPIO.output(RELAY_PIN, GPIO.LOW)
                    time.sleep(1)
                else:
                    # If the state is the same anyway, just let it through
                    # so our lil raspberry pi is not exhausted
                    time.sleep(1)
            elif timeRemaining != 0:
                if doorIsLocked != False:
                    doorIsLocked = False
                    # Turn on the relay to cut power to the maglock (unlock)
                    GPIO.output(RELAY_PIN, GPIO.HIGH)
                    logger.info("State changed to unlocked")
                    time.sleep(1)
                else:
                    time.sleep(1)
        elif guestMode:
            if doorIsLocked != False:
                doorIsLocked = False
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                logger.info("State changed to unlocked")
                time.sleep(1)
            else:
                time.sleep(1)


# Whenever an authorized user taps their ID, the timer resets back to 15.
def changeLockState(cmd):
    global timeRemaining
    if cmd == "unlock":
        # Set the time remaining to 15 seconds
        timeRemaining = 15
    if cmd == "lock":
        # Regardless if there's still a time to enter, the countdown immediately reverts back to 0 if an unauthorized person tries to enter.
        timeRemaining = 0


def activateGuestMode():
    global keepOpen
    keepOpen = True
    
def getGuestModeStatus():
    global guestMode
    while True:
        guestMode = guestMode_QuestionMark()
        time.sleep(1)


t1 = Thread(target=countItDown)
t2 = Thread(target=lockState)
t3 = Thread(target=getGuestModeStatus)
t1.start()
t2.start()
t3.start()
