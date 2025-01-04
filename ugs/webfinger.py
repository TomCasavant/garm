import os

from flask import Blueprint, request, jsonify, make_response

from ugs.db import get_db

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

    #print(resource[5:].split('@'))
    #username, domain = resource[5:].split('@')

    domain = os.getenv('BASE_URL').replace('https://', '')
    if resource[5:].count('@') == 2:
        username = resource[5:].split('@')[1]
    else:
        username = resource[5:].split('@')[0]

    print(f"Searching for {username} in domain {domain}")

    #domain = domain.strip()

    db = get_db()
    # DROP TABLE IF EXISTS actor;
    # CREATE TABLE actor (
    #     ugs_id TEXT PRIMARY KEY,
    #     profile_image TEXT,
    #     profile_url TEXT,
    #     steam_id TEXT,
    #     created_at TEXT,
    #     steam_name TEXT,
    #     public_key TEXT,
    #     private_key TEXT
    # );
    #obj = db.execute(
    #    f'SELECT * FROM actor WHERE steam_name = ?', (username,)).fetchone()
    # Username could be steam_name or ugs_id
    obj = db.execute(
        f'SELECT * FROM actor WHERE steam_name = ? OR ugs_id = ?', (username, username)).fetchone()

    if obj is None:
        return jsonify({'error': 'User not found'}), 404

    base_url = os.getenv('BASE_URL')

    response = {
        'subject': f"acct:{username}@{domain}",
        'aliases': [f"{base_url}/user/{obj['ugs_id']}"],
        'links': [ {
            'rel': 'self',
            'type': 'application/activity+json',
            'href': f"{base_url}/user/{obj['ugs_id']}"
        }]
    }
    response = jsonify(response)
    response.headers['Content-Type'] = 'application/jrd+json'
    response.headers['Access-Control-Allow-Origin'] = "*"

    return response
