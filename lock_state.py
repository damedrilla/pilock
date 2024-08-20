import RPi.GPIO as GPIO
from threading import Thread
import time
# Set the GPIO mode (BCM or BOARD)
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin controlled the electromagnetic lock via the relay module
RELAY_PIN = 4

# Set the relay pin as an output pin
GPIO.setup(RELAY_PIN, GPIO.OUT)
#Time remaining until the door locks again
#This is the condition if the door is locked or otherwise (>0 = unlocked)
timeRemaining = 0

#For lock state change detection in lockstate() method (true means door is locked)
doorIsLocked = True

#There is no way to interrupt a time.sleep() in Python so this is the workaround.
#timeRemaining decrements every loop. An iteration lasts a second
def countItDown():
  global timeRemaining
  while True:
    if timeRemaining != 0:
      timeRemaining -= 1
      print(str(timeRemaining) + " seconds remaining")
      time.sleep(1)
    else:
      print("No time left!")
      time.sleep(1)
      continue
    
def lockState():
  global doorIsLocked
  while True:
    if timeRemaining == 0:
      if doorIsLocked != True:
        doorIsLocked = True
        #Send a signal to the relay to lock the thing
        print('State changed to locked')
        GPIO.output(RELAY_PIN, GPIO.LOW)
        time.sleep(1)
      else:
        print('Locked')
        time.sleep(1)
    else:
      if doorIsLocked != False:
        doorIsLocked = False
        #Send a signal to the relay to lock the thing
        print('State changed to unlocked')
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        time.sleep(1)
      else:
        print('Unlocked')
        time.sleep(1)

def changeLockState(cmd):
  global timeRemaining
  if cmd == 'unlock':
    #Set the time remaining to 15 seconds
    timeRemaining = 15
  if cmd == 'lock':
    #Regardless if there's still a time to enter, the countdown immediately reverts back to 0 if an unauthorized person tries to enter.
    timeRemaining = 0
    
t1 = Thread(target=countItDown)
t2 = Thread(target=lockState)
t1.start()
t2.start()