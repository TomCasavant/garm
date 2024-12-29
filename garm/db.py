from datetime import datetime

import click
from flask import g, current_app
from flask.cli import load_dotenv
import sqlite3
import uuid
import os

from garm.activitypub.signature import generate_key_pair
from garm.steam_platform import SteamPlatform
from steam_web_api import Steam

load_dotenv()
print("Loaded dotenv")
# show all environment vars
print(os.environ)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('garm.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# {
#   "player": {
#     "steamid": "76561198995017863",
#     "communityvisibilitystate": 3,
#     "profilestate": 1,
#     "personaname": "The12thChairman",
#     "profileurl": "https://steamcommunity.com/id/the12thchairman/",
#     "avatar": "https://avatars.akamai.steamstatic.com/427ef7d5f8ad7b21678f69bc8afc95786cf38fe6.jpg",
#     "avatarmedium": "https://avatars.akamai.steamstatic.com/427ef7d5f8ad7b21678f69bc8afc95786cf38fe6_medium.jpg",
#     "avatarfull": "https://avatars.akamai.steamstatic.com/427ef7d5f8ad7b21678f69bc8afc95786cf38fe6_full.jpg",
#     "avatarhash": "427ef7d5f8ad7b21678f69bc8afc95786cf38fe6",
#     "lastlogoff": 1659923870,
#     "personastate": 1,
#     "primaryclanid": "103582791429521408",
#     "timecreated": 1570311509,
#     "personastateflags": 0,
#     "loccountrycode": "US"
#   }
# }

#  DROP TABLE IF EXISTS actor;
# CREATE TABLE actor (
#     garm_id TEXT PRIMARY KEY,
#     profile_image TEXT,
#     profile_url TEXT,
#     steam_id TEXT,
#     steam_name TEXT,
#     signature TEXT,
#     key TEXT
# );

def load_screen_shots():
    db = get_db()
    steam_platform = SteamPlatform(db)
    steam_platform.load_all_screenshots()

def init_db():
    db = get_db()

    # delete the screenshot table
    db.execute('DROP TABLE IF EXISTS screenshot')
    db.commit()

    # delete the screenshot table
    db.execute('DROP TABLE IF EXISTS activity')
    db.commit()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


    '''
    # Get Steam profile information
    key = os.getenv('STEAM_API_KEY')
    if key is None:
        raise Exception('STEAM_API_KEY not found')
    steam = Steam(key)
    steam_id = os.getenv('STEAM_ID')
    if steam_id is None:
        raise Exception('STEAM_ID not found')
    profile = steam.users.get_user_details(steam_id)['player']
    print(profile)
    avatar = profile['avatarfull']
    profile_url = profile['profileurl']
    steam_name = profile['personaname']

    # 'timecreated': 1326745574
    # Convert this to ActivityPub datetime format
    unix_time = profile['timecreated']
    # Convert unix time to datetime
    #created_datetime = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%dT%H:%M:%S%z')
    # Actually we need it in "2023-12-15T00:00:00Z" format
    created_datetime = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    signature = str(uuid.uuid4())

    private_key, public_key = generate_key_pair()

    # Insert Steam profile information into database
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
    db.execute(
        'INSERT INTO actor (garm_id, profile_image, profile_url, steam_id, created_at, steam_name, public_key, private_key) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (signature, avatar, profile_url, steam_id, created_datetime, steam_name, public_key, private_key)
    )

    db.commit()'''
    steam_platform = SteamPlatform(db)
    steam_platform.update_db()



@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

@click.command('load-screenshots')
def load_screenshots_command():
    load_screen_shots()
    click.echo('Loaded screenshots.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_screenshots_command)