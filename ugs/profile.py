import os
from typing import Dict

from flask import Blueprint, jsonify, request, redirect
from pydantic import BaseModel

from ugs.models.db import db
from ugs.models.actor import Actor
from .activitypub.models.activity import Actor, PublicKey
from .models.follower import Follower

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
    def from_user_row(cls, user_row: Actor) -> "Profile":
        # Use this method to create a Profile instance from the database row
        #public_key = PublicKey(
        #    id=user_row['steam_id'],
        #    owner=user_row['steam_id'],
        #    public_key_pem="test"
        #)
        # Get base URL from current webpage
        base_url = request.base_url.rsplit('/', 2)[0]
        base_url = base_url.replace('http:', 'https:')
        url = f"{base_url}/user/{user_row.ugs_id}"
        public_key = PublicKey.model_validate({
            'id': url + '#main-key',
            'owner': url,
            'publicKeyPem': user_row.public_key.decode('utf-8')
        })

        actor = Actor.model_validate({
            'id': base_url + f"/user/{user_row.ugs_id}",
            'inbox': f"{base_url}/user/{user_row.ugs_id}/inbox",
            'outbox': f"{base_url}/user/{user_row.ugs_id}/outbox",
            'type': 'Person',
            'name': user_row.name,
            'preferredUsername': user_row.steam_name,
            'summary': f"Demo user for Untitled Gaming Social. Publishes screenshots from Steam to the fediverse",
            'discoverable': True,
            'publicKey': public_key,
            'icon': {
                'type': 'Image',
                'mediaType': 'image/jpeg',
                'url': user_row.profile_image
            },
            'url': f"{base_url}/user/{user_row.steam_name}",
            'manuallyApprovesFollowers': False,
            'attachment': [ {
                'type': 'PropertyValue',
                'name': 'Steam Profile',
                'value': f"<a href='{user_row.profile_url}'>Steam Profile</a>"
            },
            {
                'type': 'PropertyValue',
                'name': 'Source Code',
                'value': "<a href='https://github.com/TomCasavant/ugs'>https://github.com/TomCasavant/ugs</a>"
            }
            ],
            'published': user_row.created_at,
            'alsoKnownAs': [user_row.profile_url],
            'attributionDomains': [user_row.profile_url]
        })
        return actor

# if GET then redirect to steam profile
# if POST then show json of user
@bp.route('/user/<username>', methods=['GET', 'POST'])
def user(username):
    user_row = Actor.query.filter_by(ugs_id=username).first()

    if user_row is None:
        # Check if matches /users/${ugs_id}
        user_row = Actor.query.filter_by(steam_name=username).first()

        # redirect if found
        if user_row is not None:
            return redirect(f"/user/{user_row.ugs_id}")

        return jsonify({'error': 'User not found'}), 404

    profile = Profile.from_user_row(user_row)
    model_dump = profile.model_dump(mode="json", by_alias=True)
    model_dump['@context'] = ['https://www.w3.org/ns/activitystreams', 'https://w3id.org/security/v1']

    if not any(accept in request.headers.get('Accept', '') for accept in ['application/activity+json', 'application/ld+json']):
        print(request.headers.get('Accept'))
        return redirect(user_row['profile_url'])

    response = jsonify(model_dump)
    response.headers['Content-Type'] = 'application/activity+json'
    return response

@bp.route('/user/<username>/followers', methods=['GET'])
def followers(username):
    user_row = Actor.query.filter_by(steam_name=username).first()

    if user_row is None:
        return jsonify({'error': 'User not found'}), 404

    base_url = os.getenv('BASE_URL')
    followers_count = len(Follower.query.filter_by(following_id=user_row.ugs_id).all())

    response = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f"{base_url}/user/{username}/followers",
        'type': 'OrderedCollection',
        'totalItems': followers_count,
        'first': f"{base_url}/user/{username}/followers?page=1"
    }

    response = jsonify(response)
    response.headers['Content-Type'] = 'application/activity+json'
    return response
