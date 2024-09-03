from flask import Flask, json
import os
#RUN THIS SCRIPT SEPARATELY
#espeak for some reason hates sudo, it will not output any voices.
#Run the main program and this script in a parallel instead.
def endpoint():
    api = Flask(__name__)

    @api.route("/welcomeUser/<name>", methods=["GET"])
    def greetUser(name):
        os.system('play -n synth 3 sin 960 synth 3 sin fmod 1920 fade l 0 3 2.8 trim 0 1')
        speech = "welcome! " + str(name)
        os.system('/usr/bin/espeak "{}" > /dev/null 2>&1'.format(speech))
        return json.dumps({"greeted": True}), 200
    
    @api.route('/deny', methods=["GET"])
    def deny():
        os.system('play -n synth 3 sin 960 synth 3 sin fmod 1920 fade l 0 3 2.8 trim 0 1 repeat 2')
        os.system('espeak -v en "access denied" --stdout | aplay')
        return json.dumps({"denied": True}), 200
    
    @api.route('/guestModeIsOn', methods=["GET"])
    def guestModeIsOn():
        speech = "the door is open, no need to tap"
        os.system('/usr/bin/espeak "{}" > /dev/null 2>&1'.format(speech))
        return json.dumps({"notified": True}), 200
    
    @api.route('/chime', methods=['GET'])
    def chime():
        os.system('play -n synth 3 sin 960 fade l 0 3 2.8 trim 0 1')
        return json.dumps({"ear_destroyed": True}), 200
    
    @api.route("/faculty_absent", methods=['GET'])
    def absent():
        os.system('play -n synth 3 sin 960 synth 3 sin fmod 1920 fade l 0 3 2.8 trim 0 1 repeat 2')
        os.system('espeak -v en "faculty is absent" --stdout | aplay')
        return json.dumps({"denied": True}), 200
    api.run(port=5001)

endpoint()