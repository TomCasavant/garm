import os
import uuid

import click
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

from steam_web_api import Steam
from ugs.activitypub.signature import generate_key_pair
from datetime import datetime

# commit as you go
db = SQLAlchemy()

@click.command('init-db')
def init_db_command():
    db.create_all()
    # print all the new tables
    click.echo('Initialized the database.')
    # Print the location of the database file
    click.echo(db.engine.url.database)
    click.echo('Initialized the database.')
    # Load in steam profile into the actor table
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
    unix_time = profile['timecreated']
    # Convert unix time to datetime
    created_datetime = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    signature = str(uuid.uuid4())
    private_key, public_key = generate_key_pair()
    # Insert Steam profile information into database using SqlAlchemy
    from ugs.models.actor import Actor
    actor = Actor(
        ugs_id=signature,
        name=name,
        profile_image=avatar,
        profile_url=profile_url,
        steam_id=steam_id,
        created_at=created_datetime,
        steam_name=steam_name,
        public_key=public_key,
        private_key=private_key
    )
    db.session.add(actor)
    db.session.commit()

def load_screen_shots():
    from ugs.steam_platform import SteamPlatform
    steam_platform = SteamPlatform(db)
    steam_platform.load_all_screenshots()

@click.command('clear-db')
def clear_db_command():
    db.drop_all()
    click.echo('Cleared the database.')

@click.command('load-screenshots')
def load_screenshots_command():
    load_screen_shots()
    click.echo('Loaded screenshots.')

@click.command('clear-screenshots')
def clear_screenshots_command():
    from ugs.models.screenshot import Screenshot
    Screenshot.query.delete()
    db.session.commit()
    click.echo('Cleared screenshots.')

@click.command('clear-activities')
def clear_activities_command():
    from ugs.models.activity import Activity
    Activity.query.delete()
    db.session.commit()
    click.echo('Cleared activities.')


def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(clear_db_command)
    app.cli.add_command(load_screenshots_command)
    app.cli.add_command(clear_screenshots_command)
    app.cli.add_command(clear_activities_command)
