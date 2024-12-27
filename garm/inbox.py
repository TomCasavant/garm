import uuid
from datetime import datetime

import requests
from flask import Blueprint, request, jsonify, make_response

from garm.activitypub.signature import sign_and_send
from garm.db import get_db

bp = Blueprint('inbox', __name__, url_prefix='/user/<username>/inbox')


def handle_follow(db, req, username):
    print("Received follow activity")
    print("Request: ", req)
    print("Actor: ", req['actor'])
    actor_obj = db.execute(
        'SELECT * FROM actor WHERE steam_name = ?',
        (username,)
    ).fetchone()

    if actor_obj is None:
        print("Actor not found")
        return "Actor not found", 404

    # DROP TABLE IF EXISTS foreign_actor;
    # CREATE TABLE foreign_actor (
    #     ap_id TEXT PRIMARY KEY,
    #     name TEXT,
    #     preferred_username TEXT,
    #     inbox TEXT,
    #     public_key TEXT
    # );
    #
    # DROP TABLE IF EXISTS foreign_activity;
    # CREATE TABLE foreign_activity (
    #     activity_id TEXT PRIMARY KEY,
    #     activity_type TEXT,
    #     foreign_actor_id TEXT,
    #     subject_actor_guid TEXT,
    #     datetime_created TEXT,
    #     raw_activity TEXT,
    #     FOREIGN KEY(foreign_actor_id) REFERENCES foreign_actor(ap_id)
    # );

    # Check if foreign_actor is already in followers table
    print("Checking if foreign actor is already in database")
    ap_object = req['object']
    activity_type = req['type']
    external_actor = req['actor']
    foreign_activity_id = req['id']

    foreign_actor_obj = db.execute(
        'SELECT * FROM foreign_actor WHERE ap_id = ?',
        (external_actor,)
    ).fetchone()

    # Store foreign actor if not already in database
    if foreign_actor_obj is None:
        print("Fetching foreign actor")
        actor_request = requests.get(external_actor, headers={'Accept': 'application/activity+json'})
        if actor_request.status_code != 200:
            return "Failed to fetch foreign actor", 400
        foreign_actor_obj = actor_request.json()
        db.execute(
            'INSERT INTO foreign_actor (ap_id, name, preferred_username, inbox, public_key) VALUES (?, ?, ?, ?, ?)',
            (foreign_actor_obj['id'], foreign_actor_obj['name'], foreign_actor_obj['preferredUsername'],
             foreign_actor_obj['inbox'], foreign_actor_obj['publicKey']['publicKeyPem'])
        )
        db.commit()
    else:
        foreign_actor_obj = {
            'ap_id': foreign_actor_obj['ap_id'],
            'name': foreign_actor_obj['name'],
            'preferred_username': foreign_actor_obj['preferred_username'],
            'inbox': foreign_actor_obj['inbox'],
            'public_key': foreign_actor_obj['public_key']
        }

    print("Foreign actor object: ", foreign_actor_obj)
    #TODO: Validate public key

    # Log the new follow activity
    # Set datetime to right now
    activity_datetime = datetime.now().isoformat()
    raw_json = str(req)
    db.execute(
        'INSERT INTO foreign_activity (activity_id, activity_type, foreign_actor_id, subject_actor_guid, datetime_created, raw_activity) VALUES (?, ?, ?, ?, ?, ?)',
        (foreign_activity_id, activity_type, foreign_actor_obj['ap_id'], username, activity_datetime, raw_json)
    )
    db.commit()

    accept_guid = uuid.uuid4()
    #base_url = request.base_url.rsplit('/', 2)[0]
    #base_url = base_url.replace('http:', 'https:')
    # Base URL should be just the domain
    base_url = request.base_url.rsplit('/', 3)[0]
    base_url = base_url.replace('http:', 'https:')
    print("BASE URL: ", base_url)

    activity_id = f"{base_url}/activities/{accept_guid}"
    accept_url = f"{base_url}/user/{actor_obj['steam_name']}/inbox/{accept_guid}"
    accept = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'type': 'Accept',
        'actor': f"{base_url}/user/{actor_obj['steam_name']}",
        'object': ap_object,
        'to': [external_actor],
        'id': activity_id,
        'published': activity_datetime
    }
    print("Accept activity: ", accept)
    sender_key = f"{ap_object}#main-key"
    # sign and Send the message
    sign_and_send(
        accept,
        actor_obj['private_key'],
        foreign_actor_obj['inbox'],
        sender_key
    )

    # DROP TABLE IF EXISTS activity;
    # CREATE TABLE activity (
    #     guid TEXT PRIMARY KEY,
    #     actor_guid TEXT,
    #     activity_type TEXT,
    #     object_guid TEXT,
    #     activity_json TEXT,
    #     FOREIGN KEY(actor_guid) REFERENCES actor(steam_name,
    #     FOREIGN KEY(object_guid) REFERENCES activity(guid)
    # );

    # Store the activity in the database
    db.execute(
        'INSERT INTO activity (guid, actor_guid, activity_type, object_guid, activity_json) VALUES (?, ?, ?, ?, ?)',
        (str(accept_guid), actor_obj['steam_name'], 'Accept', foreign_activity_id, str(accept))
    )
    db.commit()

    return make_response("Follow activity processed", 200)


@bp.route('', methods=['GET', 'POST'])
def inbox(username):
    print(f"Received request for {username}'s inbox")
    # Handles AP requests to the inbox
    db = get_db()
    actor_obj = db.execute(
        'SELECT * FROM actor WHERE steam_name = ?',
        (username,)
    ).fetchone()

    if actor_obj is None:
        return "Actor not found", 404

    ap_object = request.json.get('object')
    activity_type = request.json['type']
    external_actor = request.json['actor']
    foreign_activity_id = request.json['id']

    if activity_type is None:
        return "Missing activity type", 400

    response = None
    match activity_type:
        case 'Follow':
            response = handle_follow(db, request.json, username)
        case 'Undo':
            print("Undo activity")
            print("External Actor:", external_actor)
            print("AP Object:", ap_object)
        case _:
            print("Unknown activity type")
            print("External Actor:", external_actor)
            print("AP Object:", ap_object)

    if response is not None:
        return response, 202

    return make_response('', 200)