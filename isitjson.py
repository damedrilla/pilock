from getCurrentSchedule import currentSchedule
import json
sc = currentSchedule(True)
print(type(sc)) 
try:
    sc['status']
except Exception as e:
    print(e)
    sc = json.loads(sc)
    try:
        print(sc['status'])
    except Exception:
        print(sc['instructor'])
    print(type(sc))
sc = currentSchedule(False)
print(type(sc))
try:
    try:
        print(sc['status'])
    except Exception:
        print(sc['schedule'][0]['instructor'])
except Exception as e:
    print(e)