import os
import time
import re
from pymongo import MongoClient
import json

MENTION_REGEX = "^<@(|[WU].+?)\|.*>(.*)"

def connect(config):
    connection = MongoClient(config['db_url'], config['db_port'])
    db = connection[config['db_name']]
    db.authenticate(config['db_user'], config['db_pass'])
    
    return db.score

def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else ("", "")

def get_user_info(user_id, slack_client):
    return slack_client.api_call(
        "users.info",
        user=user_id,
        include_locale=True,
    )

def handle_scoreboard(command, author, collection, client):
    user_id, message = parse_direct_mention(command)
    tokens = message.split()
    print("Message: " + message)
    if len(tokens) > 0 and len(user_id) > 0:
        try:
            userinfo = get_user_info(user_id, client)
            authorinfo = get_user_info(author, client)
            amount = float(tokens[0])
            description = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            entity = {
                "giver": authorinfo["user"],
                "receiver": userinfo["user"],
                "amount": amount,
                "description": description 
            }
            collection.insert(entity)
            return "%s has given %.2f points to %s for %s" % (authorinfo["user"]["real_name"], amount, userinfo["user"]["real_name"], description)
        except:
            return "Syntax: @User <amount> <description>"
    elif len(user_id) > 0:
        userinfo = get_user_info(user_id, client)
        authorinfo = get_user_info(author, client)
        entity = {
            "giver": authorinfo["user"],
            "receiver": userinfo["user"],
            "amount": 1,
            "description": "" 
        }
        collection.insert(entity)
        return "%s has given %.2f points to %s" % (authorinfo["user"]["real_name"], 1, userinfo["user"]["real_name"])
    else:
        message = "```%-20s %s\n" % ("User", "Score")
        for x in collection.aggregate([ {"$group": { "_id": "$receiver.id", "total": { "$sum": "$amount" }, "name": { "$first": "$receiver.real_name" } } }]):
            print("%-20s %.2f\n" % (x["name"], x["total"]))
            message += "%-20s %.2f\n" % (x["name"], x["total"])
        return message + "```"

