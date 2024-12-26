from flask import Blueprint, request, jsonify, make_response

from garm.db import get_db

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

    username, domain = resource[5:].split('@')

    domain = domain.strip()

    db = get_db()
    # DROP TABLE IF EXISTS actor;
    # CREATE TABLE actor (
    #     garm_id TEXT PRIMARY KEY,
    #     profile_image TEXT,
    #     profile_url TEXT,
    #     steam_id TEXT,
    #     created_at TEXT,
    #     steam_name TEXT,
    #     public_key TEXT,
    #     private_key TEXT
    # );
    obj = db.execute(
        f'SELECT * FROM actor WHERE steam_name = ?', (username,)).fetchone()

    if obj is None:
        return jsonify({'error': 'User not found'}), 404
    base_url = request.base_url.rsplit('/', 2)[0]
    # replace with https
    base_url = base_url.replace('http:', 'https:')
    response = {
        'subject': f"acct:{username}@{domain}",
        'aliases': [f"{base_url}/user/{username}"],
        'links': [ {
            'rel': 'self',
            'type': 'application/activity+json',
            'href': f"{base_url}/user/{username}"
        }]
    }

    return jsonify(response)