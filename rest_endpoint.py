from flask import Flask, json

def endpoint():
    api = Flask(__name__)
    @api.route('/unlock', methods=['POST'])
    def unlockDoor():
        print('Door unlocked successfully')
        return json.dumps({"success": True}), 201

    api.run()