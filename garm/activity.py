import re

from flask import Blueprint, request, jsonify, make_response, redirect

from garm.db import get_db
from garm.steam_platform import STEAM_FILEPATH

bp = Blueprint('activities', __name__, url_prefix='/activities')

@bp.route('/<path:activity_id>', methods=['GET', 'POST'])
def get_activity(activity_id):
    print(f"Getting activity {activity_id}")
    db = get_db()

    # if the url contains the STEAM_FILEPATH, then extract the id and check if it exists in the database
    # regex extract the id from the url
    # STEAM_FILEPATH = "https://steamcommunity.com/sharedfiles/filedetails/?id={}"
    # TODO: I think we should probably just store the full URL in the database
    if activity_id in STEAM_FILEPATH:
        full_activity_url = request.full_path.lstrip('/activities/').rstrip('?')
        match = re.search(r'\?id=(\d+)', full_activity_url)
        if match:
            screenshot_id = match.group(1)
            activity = db.execute(
                'SELECT * FROM activity WHERE screenshot_id = ?', (screenshot_id,)
            ).fetchone()
        else:
            return "Invalid Steam URL format", 400
    else:
        activity = db.execute(
            'SELECT * FROM activity WHERE guid = ?', (activity_id,)
        ).fetchone()

    if activity is None:
        print("Activity not found")
        return "Activity not found", 404

    if request.method == 'GET':
        if any(accept not in request.headers.get('Accept') for accept in ['application/activity+json', 'application/ld+json']):
            screenshot_id = activity['screenshot_id']
            if screenshot_id:
                return redirect(STEAM_FILEPATH.format(screenshot_id))

        json_str = activity['activity_json']
        activity_dict = eval(json_str)

        activity_dict['@context'] = ['https://www.w3.org/ns/activitystreams', 'https://w3id.org/security/v1']
        response = jsonify(activity_dict)
        response.headers['Content-Type'] = 'application/activity+json'
        return response

    if request.method == 'POST':
        return make_response('', 202)