from flask import Blueprint, request, jsonify, make_response
from ugs.models.db import db
from ugs.models.screenshot import Screenshot
bp = Blueprint('base', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
def base():
    screenshots = Screenshot.query.order_by(Screenshot.time_created.desc()).limit(10).all()

    html = "<h1>Recent Screenshots</h1>"
    for screenshot in screenshots:
        html += f"<h2>{screenshot.app_name}</h2>"
        html += f"<img src='{screenshot.image_url}' alt='{screenshot.app_name}'><br>"

    return make_response(html, 200)