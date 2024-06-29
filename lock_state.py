from threading import Thread
import time

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
        time.sleep(1)
      else:
        print('Locked')
        time.sleep(1)
    else:
      if doorIsLocked != False:
        doorIsLocked = False
        #Send a signal to the relay to lock the thing
        print('State changed to unlocked')
        time.sleep(1)
      else:
        print('Unlocked')
        time.sleep(1)

def changeLockState(cmd):
  global timeRemaining
  if cmd == 'unlock':
    #Set the time remaining to 30 seconds
    timeRemaining = 30
  if cmd == 'lock':
    #Regardless if there's still a time to enter, the countdown immediately reverts back to 0 if an unauthorized person tries to enter.
    timeRemaining = 0
    
t1 = Thread(target=countItDown)
t2 = Thread(target=lockState)
t1.start()
t2.start()