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
        g.db = sqlite3.connect('ugs.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def load_screen_shots():
    db = get_db()
    steam_platform = SteamPlatform(db)
    steam_platform.load_all_screenshots()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

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
    name = os.getenv('NAME')

    # 'timecreated': 1326745574
    unix_time = profile['timecreated']
    # Convert unix time to datetime
    created_datetime = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    signature = str(uuid.uuid4())

    private_key, public_key = generate_key_pair()

    # Insert Steam profile information into database
    db.execute(
        'INSERT INTO actor (ugs_id, name, profile_image, profile_url, steam_id, created_at, steam_name, public_key, private_key) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (signature, name, avatar, profile_url, steam_id, created_datetime, steam_name, public_key, private_key)
    )

    db.commit()

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

@click.command('load-screenshots')
def load_screenshots_command():
    load_screen_shots()
    click.echo('Loaded screenshots.')

@click.command('clear-screenshots')
def clear_screenshots_command():
    db = get_db()
    db.execute('DELETE FROM screenshot')
    db.commit()
    click.echo('Cleared screenshots.')

@click.command('clear-activities')
def clear_activities_command():
    # ONLY USE FOR TESTING, WILL DELETE ALL ACTIVITIES
    db = get_db()
    db.execute('DELETE FROM activity')
    db.commit()
    click.echo('Cleared activities.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_screenshots_command)
    app.cli.add_command(clear_screenshots_command)
    app.cli.add_command(clear_activities_command)