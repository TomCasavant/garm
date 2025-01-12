from flask import Blueprint, request, jsonify, make_response, render_template

from ugs.models.activity import Activity
from ugs.models.db import db
from ugs.models.screenshot import Screenshot
bp = Blueprint('base', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def base():
    page = request.args.get('page', default=1, type=int)
    offset = page * 10 - 10
    screenshots = Screenshot.query.order_by(Screenshot.time_created.desc()).limit(10).offset(offset).all()
    activities = Activity.query.filter(
        Activity.screenshot_id.in_([s.steam_id for s in screenshots]),
        Activity.activity_type == 'Note'
    ).all()
    activity_map = {s.steam_id: None for s in screenshots}
    for activity in activities:
        activity_map[activity.screenshot_id] = activity

    return render_template('home.html', screenshots=screenshots, activity_map=activity_map)
