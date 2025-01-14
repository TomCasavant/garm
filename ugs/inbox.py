import uuid
from datetime import datetime

import requests
from flask import Blueprint, request, jsonify, make_response

from ugs.activitypub.signature import sign_and_send
from ugs.models.activity import Activity
from ugs.models.db import db
from ugs.models.actor import Actor
from ugs.models.follower import Follower
from ugs.models.foreign_activity import ForeignActivity
from ugs.models.foreign_actor import ForeignActor
import uuid

bp = Blueprint('inbox', __name__, url_prefix='/user/<username>/inbox')


def handle_follow(req, username):
    actor_obj = Actor.query.filter_by(ugs_id=username).first()
    if actor_obj is None:
        print("Actor not found")
        response = jsonify({'error': 'Actor not found'})
        response.status_code = 404
        return response

    ap_object = req['object']
    activity_type = req['type']
    external_actor = req['actor']
    foreign_activity_id = req['id']

    foreign_actor_obj = ForeignActor.query.filter_by(ap_id=external_actor).first()
    # Store foreign actor if not already in database
    if foreign_actor_obj is None:
        print("Fetching foreign actor")
        actor_request = requests.get(external_actor, headers={'Accept': 'application/activity+json'})
        if actor_request.status_code != 200:
            response = jsonify({'error': 'Failed to fetch foreign actor'})
            response.status_code = 400
            return response
        foreign_actor_obj = actor_request.json()

        # Store the foreign actor in the database
        new_actor = ForeignActor(
            ap_id=foreign_actor_obj['id'],
            name=foreign_actor_obj['name'],
            preferred_username=foreign_actor_obj['preferredUsername'],
            inbox=foreign_actor_obj['inbox'],
            public_key=foreign_actor_obj['publicKey']['publicKeyPem']
        )
        db.session.add(new_actor)
        db.session.commit()
        foreign_actor_obj = ForeignActor.query.filter_by(ap_id=external_actor).first()

    foreign_actor_obj = {
        'ap_id': foreign_actor_obj.ap_id,
        'name': foreign_actor_obj.name,
        'preferred_username': foreign_actor_obj.preferred_username,
        'inbox': foreign_actor_obj.inbox,
        'public_key': foreign_actor_obj.public_key
    }

    print("Foreign actor object: ", foreign_actor_obj)
    #TODO: Validate public key

    # Log the new follow activity
    # Set datetime to right now
    activity_datetime = datetime.now().isoformat()
    raw_json = str(req)
    print(foreign_actor_obj)
    new_activity = ForeignActivity(
        activity_id=foreign_activity_id,
        activity_type=activity_type,
        foreign_actor_id=foreign_actor_obj['ap_id'],
        subject_actor_guid=username,
        datetime_created=activity_datetime,
        raw_activity=raw_json
    )
    db.session.add(new_activity)
    db.session.commit()

    accept_guid = uuid.uuid4()

    # Base URL should be just the domain
    base_url = request.base_url.rsplit('/', 3)[0]
    base_url = base_url.replace('http:', 'https:')
    print("BASE URL: ", base_url)

    activity_id = f"{base_url}/activities/{accept_guid}"
    accept = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'type': 'Accept',
        'actor': f"{base_url}/user/{actor_obj.ugs_id}",
        'object': req['id'],
        'to': [external_actor],
        'id': activity_id,
        'published': activity_datetime
    }
    print("Accept activity: ", accept)
    sender_key = f"{ap_object}#main-key"
    # sign and Send the message
    sign_and_send(
        accept,
        actor_obj.private_key,
        foreign_actor_obj['inbox'],
        sender_key
    )

    # Store the activity in the database
    #     db.execute(
    #         'INSERT INTO activity (guid, actor_guid, activity_type, object_guid, activity_json) VALUES (?, ?, ?, ?, ?)',
    #         (str(accept_guid), actor_obj['steam_name'], 'Accept', foreign_activity_id, str(accept))
    #     )
    #     db.commit()
    new_activity = Activity(
        guid=str(accept_guid),
        actor_guid=actor_obj.ugs_id,
        activity_type='Accept',
        object_guid=foreign_activity_id,
        activity_json=str(accept),
        screenshot_id=None
    )
    db.session.add(new_activity)
    db.session.commit()

    # TODO: Check if successful?
    # Store the follow activity in the followers table
    new_follower = Follower(
        follower_id=foreign_actor_obj['ap_id'],
        following_id=actor_obj.ugs_id
    )
    db.session.add(new_follower)
    db.session.commit()

    return make_response("Follow activity processed", 200)


@bp.route('', methods=['GET', 'POST'])
def inbox(username):
    print(f"Received request for {username}'s inbox")
    # Handles AP requests to the inbox
    actor_obj = Actor.query.filter_by(ugs_id=username).first()

    if actor_obj is None:
        print("Actor not found")
        print("Username:", username)
        # Print first row of the actor table
        actor_obj = Actor.query.first()
        print("First row of actor table:", actor_obj)
        response = jsonify({'error': 'Actor not found'})
        response.status_code = 404
        return response

    ap_object = request.json.get('object')
    activity_type = request.json['type']
    external_actor = request.json['actor']
    foreign_activity_id = request.json['id']

    if activity_type is None:
        print("Missing activity type")
        response = jsonify({'error': 'Missing activity type'})
        response.status_code = 400
        return response

    response = None
    match activity_type:
        case 'Follow':
            print("handle follow activity")
            response = handle_follow(request.json, username)
        case 'Undo':
            print("Undo activity")
            print("External Actor:", external_actor)
            print("AP Object:", ap_object)
            # Undo activity
            if ap_object['type'] == 'Follow':
                follower = Follower.query.filter_by(follower_id=external_actor, following_id=actor_obj.ugs_id).first()
                if follower is None:
                    print("Follower not found")
                    response = jsonify({'error': 'Follower not found'})
                    response.status_code = 404
                    return response
                db.session.delete(follower)
                db.session.commit()
            else:
                # Unknown undo activity
                # Add to table with type Undo
                new_activity = ForeignActivity(
                    activity_id=str(uuid.uuid4()),
                    activity_type='Undo',
                    foreign_actor_id=None,
                    subject_actor_guid=None,
                    datetime_created=None,
                    raw_activity=str(request.json)
                )
                db.session.add(new_activity)
                db.session.commit()
        case _:
            print("Unknown activity type")
            print("External Actor:", external_actor)
            print("AP Object:", ap_object)
            new_activity = ForeignActivity(
                activity_id=str(uuid.uuid4()),
                activity_type=activity_type,
                foreign_actor_id=None,
                subject_actor_guid=None,
                datetime_created=None,
                raw_activity=str(request.json)
            )
            db.session.add(new_activity)
            db.session.commit()
            print("Added unknown activity to database")

    if response is not None:
        return response, 202

    return make_response('', 200)