from flask import Flask, json, jsonify, request
from lock_state import changeLockState
from internetCheck import isInternetUp
from flask_cors import CORS, cross_origin
from LCDcontroller import remotelyUnlocked
from espeakEventListener import chime
import requests
from facPrescenceController import changeFacultyPrescenceState, getFacultyPrescenceState, getAllPrescenceData

from getCurrentSchedule import currentSchedule


def endpoint():

    api = Flask(__name__)
    CORS(api, support_credentials=True)

    @api.route("/unlock", methods=["POST"])
    def unlockDoor():
        changeLockState("unlock")
        remotelyUnlocked()
        chime()
        print("Door unlocked successfully")
        try:
            try:
                changeFacultyPrescenceState()
                _data = getAllPrescenceData()
                requests.post('https://www.pilocksystem.live/api/attendinst/' + str(_data['uid']).zfill(10), timeout=2)
            except Exception as e:
                changeFacultyPrescenceState()
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
