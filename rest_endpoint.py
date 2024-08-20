from flask import Flask, json, jsonify, request
from lock_state import changeLockState
from internetCheck import isInternetUp
from flask_cors import CORS, cross_origin
import requests


from getCurrentSchedule import currentSchedule


def endpoint():

    api = Flask(__name__)
    CORS(api, support_credentials=True)

    @api.route("/unlock", methods=["POST"])
    def unlockDoor():
        changeLockState("unlock")
        print("Door unlocked successfully")
        try:
            try:
                data = open("backup_data/instructor_prescence.json")
                data_parsed = json.load(data)
                requests.post('https://www.pilocksystem.live/api/attendinst/' + str(data_parsed['uid']).zfill(10), timeout=2)
                data_parsed["isInstructorPresent"] = 1
                data.close()
                with open("backup_data/instructor_prescence.json", "w") as f:
                    json.dump(data_parsed, f)
                f.close()
            except Exception as e:
                data = open("backup_data/instructor_prescence.json")
                data_parsed = json.load(data)
                data_parsed["isInstructorPresent"] = 1
                data.close()
                with open("backup_data/instructor_prescence.json", "w") as f:
                    json.dump(data_parsed, f)
                f.close()
        except:
            pass
        return json.dumps({"success": True}), 201

    @api.route("/schedule", methods=["GET"])
    @cross_origin(supports_credentials=True)
    def getSched():
        return jsonify(currentSchedule()), 200

    @api.route("/validate", methods=["POST"])
    def validate():
        try:
            form_data = request.json
            sch = currentSchedule()
            if (
                form_data["sub"] == sch["subject"]
                and form_data["inst"] == sch["instructor"]
            ):
                return jsonify({"res": "ok"})
        except:
            return jsonify({"res": "deny"})

    @api.route("/sanity_check", methods=["GET"])
    @cross_origin(supports_credentials=True)
    def getInternet():
        return jsonify({"localMode": isInternetUp()}), 200

    api.run(host="0.0.0.0", port=5000)
