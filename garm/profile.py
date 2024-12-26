from typing import Dict

from flask import Blueprint, jsonify, request, redirect
from pydantic import BaseModel

from garm.db import get_db
from .activitypub.models.activity import Actor, PublicKey

bp = Blueprint('user', __name__, url_prefix='/')

# class PublicKey(BaseModel):
#     id: str
#     owner: str
#     public_key_pem: str = Field(alias='publicKeyPem')
class Profile(Actor):
    inbox: str
    outbox: str
    type: str
    name: str
    preferred_username: str
    summary: str
    discoverable: bool

    @classmethod
    def from_user_row(cls, user_row: dict) -> "Profile":
        # Use this method to create a Profile instance from the database row
        #public_key = PublicKey(
        #    id=user_row['steam_id'],
        #    owner=user_row['steam_id'],
        #    public_key_pem="test"
        #)
        # Get base URL from current webpage
        base_url = request.base_url.rsplit('/', 2)[0]
        base_url = base_url.replace('http:', 'https:')
        url = f"{base_url}/user/{user_row['steam_name']}"
        public_key = PublicKey.model_validate({
            'id': url + '#main-key',
            'owner': url,
            'publicKeyPem': user_row['public_key'].decode('utf-8')
        })

        actor = Actor.model_validate({
            'id': base_url + f"/user/{user_row['steam_name']}",
            'inbox': f"{base_url}/user/{user_row['steam_name']}/inbox",
            'outbox': f"{base_url}/user/{user_row['steam_name']}/outbox",
            'type': 'Person',
            'name': user_row['steam_name'],
            'preferredUsername': user_row['steam_name'],
            'summary': "Summary test",
            'discoverable': True,
            'publicKey': public_key,
            'icon': {
                'type': 'Image',
                'mediaType': 'image/jpeg',
                'url': user_row['profile_image']
            },
            'url': f"{base_url}/user/{user_row['steam_name']}",
            'manuallyApprovesFollowers': False,
            'attachment': [ {
                'type': 'PropertyValue',
                'name': 'Steam Profile',
                'value': user_row['profile_url']
            }],
            'published': user_row['created_at'],
            'alsoKnownAs': [user_row['profile_url']],
            'attributionDomains': [user_row['profile_url']]
        })
        return actor


#@bp.route('/user/<username>', methods=['GET'])
#def user(username):
#    db = get_db()
#    user_row = db.execute(
#        'SELECT * FROM actor WHERE steam_name = ?',
#        (username,)
#    ).fetchone()

#    if user_row is None:
#        return jsonify({'error': 'User not found'}), 404

#    user = dict(user_row)
#    return jsonify(user)

# if GET then redirect to steam profile
# if POST then show json of user
@bp.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    db = get_db()
    user_row = db.execute(
        'SELECT * FROM actor WHERE steam_name = ?',
        (username,)
    ).fetchone()

    if user_row is None:
        return jsonify({'error': 'User not found'}), 404

    profile = Profile.from_user_row(user_row)
    model_dump = profile.model_dump(mode="json", by_alias=True)
    # Add context             @context=['https://www.w3.org/ns/activitystreams', 'https://w3id.org/security/v1']
    model_dump['@context'] = ['https://www.w3.org/ns/activitystreams', 'https://w3id.org/security/v1']
    #return jsonify(model_dump)
    #user = dict(user_row)
    #if request.method == 'GET':
    #    return redirect(user['profile_url'])
    # set headers to 'application/activity+json'
    response = jsonify(model_dump)
    response.headers['Content-Type'] = 'application/activity+json'
    return response