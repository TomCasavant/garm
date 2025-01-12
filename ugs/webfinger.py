import os

from flask import Blueprint, request, jsonify, make_response
from flask.cli import load_dotenv

from ugs.models.actor import Actor
from ugs.models.db import db
from dotenv import load_dotenv
bp = Blueprint('webfinger', __name__, url_prefix='/.well-known/webfinger')

@bp.route('', methods=['GET'])
def webfinger():
    print(request)
    print(request.args)
    print(request.args.get('resource'))
    print(request.headers)
    resource = request.args.get('resource')
    if not resource:
        return jsonify({'error': 'No resource provided'}), 400

    if not resource.startswith('acct:'):
        return jsonify({'error': 'Invalid resource format'}), 400

    print(load_dotenv())
    domain = os.getenv('BASE_URL').replace('https://', '').strip('/')
    if resource[5:].count('@') == 2:
        username = resource[5:].split('@')[1]
    else:
        username = resource[5:].split('@')[0]

    print(f"Searching for {username} in domain {domain}")

    # Username could be steam_name or ugs_id
    obj = Actor.query.filter_by(steam_name=username).first()
    if obj is None:
        return jsonify({'error': 'User not found'}), 404

    base_url = os.getenv('BASE_URL').strip('/')

    response = {
        'subject': f"acct:{username}@{domain}",
        'aliases': [f"{base_url}/user/{obj.ugs_id}"],
        'links': [ {
            'rel': 'self',
            'type': 'application/activity+json',
            'href': f"{base_url}/user/{obj.ugs_id}"
        }]
    }
    response = jsonify(response)
    response.headers['Content-Type'] = 'application/jrd+json'
    response.headers['Access-Control-Allow-Origin'] = "*"

    return response
