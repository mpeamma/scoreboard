import json
from flask import jsonify

import util

def verify_web_hook(form):
    if not form or form.get('token') != config['SLACK_TOKEN']:
        raise ValueError('Invalid request/credentials.')

def scoreboard(request):
    print(request.form)
    if request.method != 'POST':
        return 'Only POST requests are accepted', 405
    
    with open('config.json', 'r') as f:
        data = f.read()
    config = json.loads(data)

    #verify_web_hook(request.form)
    score = util.connect(config)
    message = {
        "text": util.handle_scoreboard(request.form.get("text"), request.form.get("user_id"), score),
        "response_type": "in_channel"
    }
    return jsonify(message)
