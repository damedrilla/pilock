from flask import Flask, json, jsonify
from lock_state import changeLockState
from getCurrentSchedule import currentSchedule

def endpoint():
    api = Flask(__name__)

    @api.route("/unlock", methods=["POST"])
    def unlockDoor():
        changeLockState("unlock")
        print("Door unlocked successfully")
        return json.dumps({"success": True}), 201
    @api.route("/schedule", methods=['GET'])
    def getSched():
        return jsonify(currentSchedule()), 200
        
    api.run(host="0.0.0.0", port=5000)
