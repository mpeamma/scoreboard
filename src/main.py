import json
from flask import jsonify
from slackclient import SlackClient

import util

def verify_web_hook(form, config):
    if not form or form.get('token') != config['SLACK_TOKEN']:
        raise ValueError('Invalid request/credentials.')

def scoreboard(request):
    print(request.form)
    if request.method != 'POST':
        return 'Only POST requests are accepted', 405
    
    with open('config.json', 'r') as f:
        data = f.read()
    config = json.loads(data)
    client = SlackClient(config["SLACK_BOT_TOKEN"])

    verify_web_hook(request.form, config)
    score = util.connect(config)
    message = {
        "text": util.handle_scoreboard(request.form.get("text"), request.form.get("user_id"), score, client),
        "response_type": "in_channel"
    }
    return jsonify(message)
