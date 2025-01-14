import os
import re
from datetime import datetime

from flask import Blueprint, request, jsonify, make_response, redirect

from ugs.activitypub.models.activity import AudienceType
from ugs.activitypub.signature import sign_and_send
from ugs.models.actor import Actor
from ugs.models.db import db
from ugs.models.follower import Follower
from ugs.models.foreign_actor import ForeignActor
from ugs.steam_platform import STEAM_FILEPATH
from ugs.models.activity import Activity

bp = Blueprint('activities', __name__, url_prefix='/activities')
base_url = os.getenv('BASE_URL')
base_url = base_url.strip('/')

@bp.route('/<path:activity_id>', methods=['GET', 'POST'])
def activity(activity_id):
    print(f"Getting activity {activity_id}")

    # if the url contains the STEAM_FILEPATH, then extract the id and check if it exists in the database
    # regex extract the id from the url
    # STEAM_FILEPATH = "https://steamcommunity.com/sharedfiles/filedetails/?id={}"
    # TODO: I think we should probably just store the full URL in the database
    if activity_id in STEAM_FILEPATH:
        full_activity_url = request.full_path.lstrip('/activities/').rstrip('?')
        match = re.search(r'\?id=(\d+)', full_activity_url)
        if match:
            screenshot_id = match.group(1)
            activity = Activity.query.filter_by(screenshot_id=screenshot_id).first()
        else:
            return "Invalid Steam URL format", 400
    else:
        # Check if path contains /create
        # if it contains /create then only get the activity with activity_type CREATE
        if '/create' in activity_id:
            activity_id = activity_id.replace('/create', '')
            guid = f"{activity_id}-create"
            activity = Activity.query.filter_by(guid=guid).first()
        else:
            activity = Activity.query.filter_by(guid=activity_id).first()

    if activity is None:
        print("Activity not found")
        return "Activity not found", 404

    if request.method == 'GET':
        print(request.headers)
        try:
            if not any(accept in request.headers.get('Accept', '') for accept in ['application/activity+json', 'application/ld+json']):
                print("Redirecting to Steam")
                screenshot_id = activity.screenshot_id
                print(f"Screenshot ID: {screenshot_id}")
                if screenshot_id:
                    return redirect(STEAM_FILEPATH.format(screenshot_id))
        except Exception as e:
            print(f"Error: {e} - Accept headers not included?")

        json_str = activity.activity_json
        activity_dict = eval(json_str)

        activity_dict['@context'] = ['https://www.w3.org/ns/activitystreams', 'https://w3id.org/security/v1']
        response = jsonify(activity_dict)
        response.headers['Content-Type'] = 'application/activity+json'
        return response

    if request.method == 'POST':
        return make_response('', 202)


def send_activity(activity):
    # Check if the activity already has a corresponding "Create" activity
    create_activity_guid = f"{activity.guid}-create"
    create_activity = Activity.query.filter_by(guid=create_activity_guid).first()

    print(f"Activity Exists: {create_activity}")

    # Retrieve the actor associated with the activity
    actor_obj = Actor.query.filter_by(ugs_id=activity.actor_guid).first()

    print(f"Actor: {actor_obj}")

    if actor_obj is None:
        return None

    # Get all followers of the actor
    followers = Follower.query.filter_by(following_id=actor_obj.ugs_id).all()
    print(f"Sending to all {len(followers)} followers")

    for follower in followers:
        # Retrieve the follower from the ForeignActor table
        ap_id = follower.follower_id
        foreign_actor_obj = ForeignActor.query.filter_by(ap_id=ap_id).first()
        if not foreign_actor_obj:
            print(f"Foreign actor not found for follower ID: {ap_id}")
            continue

        inbox = foreign_actor_obj.inbox

        if create_activity:
            print("Create activity already exists, sending that one")
            # Sign and send the existing "Create" activity
            create_activity_dict = eval(create_activity.activity_json)
            sign_and_send(
                create_activity_dict,
                actor_obj.private_key,
                inbox,
                f"{base_url}/user/{actor_obj.steam_name}#main-key"
            )
        else:
            # Wrap the activity in a new "Create" activity
            create_url = f"{base_url}/activities/{activity.guid}/create"
            print(f"New create URL: {create_url}")

            # Get the current datetime in ISO 8601 format
            activity_datetime = datetime.now().isoformat()

            # Parse the original activity's JSON
            activity_json = eval(activity.activity_json)

            new_create_activity = {
                '@context': 'https://www.w3.org/ns/activitystreams',
                'type': 'Create',
                'actor': f"{base_url}/user/{actor_obj.ugs_id}",
                'object': activity_json,
                'to': [AudienceType.Public.value],
                'cc': [f"{base_url}/user/{actor_obj.ugs_id}/followers"],
                'id': create_url,
                'published': activity_datetime,
            }

            # Save the new "Create" activity in the database
            new_activity = Activity(
                guid=create_activity_guid,
                actor_guid=actor_obj.ugs_id,
                activity_type='Create',
                object_guid=activity.guid,
                activity_json=str(new_create_activity),
                screenshot_id=activity.screenshot_id,
            )
            db.session.add(new_activity)
            db.session.commit()

            # Update the create_activity variable for subsequent loops
            create_activity = new_activity

            print("Sending new create activity")

            # Sign and send the new "Create" activity
            sign_and_send(
                new_create_activity,
                actor_obj.private_key,
                inbox,
                f"{base_url}/user/{actor_obj.steam_name}#main-key"
            )
