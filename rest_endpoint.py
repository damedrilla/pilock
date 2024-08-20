from flask import Flask, json
from lock_state import changeLockState

def endpoint():
    api = Flask(__name__)
    @api.route('/unlock', methods=['POST'])
    def unlockDoor():
        changeLockState('unlock')
        print('Door unlocked successfully')
        return json.dumps({"success": True}), 201

    api.run(host='0.0.0.0' , port=5000)
endpoint()