from flask import Blueprint, request, jsonify, make_response

from garm.db import get_db

bp = Blueprint('activities', __name__, url_prefix='/activities')

@bp.route('/<activity_id>', methods=['GET', 'POST'])
def get_activity(activity_id):
    print(f"Getting activity {activity_id}")
    db = get_db()
    activity = db.execute(
        'SELECT * FROM activity WHERE guid = ?', (activity_id,)
    ).fetchone()

    if activity is None:
        print("Activity not found")
        return "Activity not found", 404

    if request.method == 'GET':
        json_str = activity['activity_json']
        activity_dict = eval(json_str)
        activity_dict['@context'] = ['https://www.w3.org/ns/activitystreams', 'https://w3id.org/security/v1']
        response = jsonify(activity_dict)
        response.headers['Content-Type'] = 'application/activity+json'
        return response

    if request.method == 'POST':
        return make_response('', 202)