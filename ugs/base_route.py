from flask import Blueprint, request, jsonify, make_response
from ugs.db import get_db
bp = Blueprint('base', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def base():
    db = get_db()
    # Return a page with the 10 most recent screenshots
    screenshots = db.execute(
        'SELECT * FROM screenshot ORDER BY time_created DESC LIMIT 10'
    ).fetchall()

    html = "<h1>Recent Screenshots</h1>"
    for screenshot in screenshots:
        html += f"<h2>{screenshot['app_name']}</h2>"
        html += f"<img src='{screenshot['image_url']}' alt='{screenshot['app_name']}'><br>"

    return make_response(html, 200)