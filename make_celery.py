import logging
import os

from ugs import create_app
from ugs.activity import send_activity
from ugs.models.activity import Activity
from ugs.models.actor import Actor
from ugs.models.db import db
from ugs.models.screenshot import Screenshot
from ugs.steam_platform import SteamPlatform

flask_app = create_app()
celery_app = flask_app.extensions['celery']
logger = logging.getLogger(__name__)

# Schedule task for every 10 minutes
# Should get the most recent 5 screenshots
# if there are screenshots that are not in the database, add them
# Then send out Create Note to all followers
def get_screenshots():
    pass

@celery_app.task
def post_screenshot():
    print("Posting screenshot")
    # Gets all the screenshots
    # Finds most recent that doesn't have a CREATE Note in the db
    # Sends out a Create Note to all followers
    #screenshots = db.execute(
    #    'SELECT * FROM screenshot ORDER BY time_created ASC'
    #).fetchall()
    screenshots = Screenshot.query.order_by(Screenshot.time_created.asc()).all()

    unposted_screenshot = None
    for screenshot in screenshots:
        screenshot_id = screenshot.steam_id
        create_activity = Activity.query.filter_by(screenshot_id=screenshot_id, activity_type='Create').first()
        if create_activity is None:
            unposted_screenshot = screenshot
            break

    if unposted_screenshot is None:
        return

    unposted_activity = Activity.query.filter_by(screenshot_id=unposted_screenshot.steam_id, activity_type='Note').first()

    send_activity(unposted_activity)

# Every 15 minutes check if there are new screenshots
@celery_app.task
def check_for_new_screenshots():
    # Get the 10 newest screenshots
    steam_platform = SteamPlatform(db)
    screenshots = steam_platform.get_screenshots()['response']['publishedfiledetails']
    # Check if the first screenshot is in the database
    newest_screenshot = screenshots[0]
    screenshot_id = newest_screenshot['publishedfileid']

    screenshot_db = Screenshot.query.filter_by(steam_id=screenshot_id).first()
    actor = Actor.query.filter_by(steam_id=os.getenv('STEAM_ID')).first()
    if screenshot_db is not None:
        print("Newest screenshot is already in the database")
        return

    # Otherwise, loop through the screenshots until we find one that is in the database
    for screenshot in screenshots:
        screenshot_id = screenshot['publishedfileid']
        screenshot_search = Screenshot.query.filter_by(steam_id=screenshot_id).first()
        if screenshot_search is not None:
            print("Found screenshot in database")
            break

        # Add the screenshot to the database
        steam_platform.add_screenshot(screenshot, actor.ugs_id)

        # Get the newly created activity
        # TODO: Can we just return the created activity? So we don't search the database as much
        activity = Activity.query.filter_by(screenshot_id=screenshot_id, activity_type='Note').first()

        # Send the activity to all followers
        send_activity(activity)


# scheudle task for every 10 minutes, share screenshot with followers
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(45*60, post_screenshot.s(), name='Post screenshots every 45 minutes')
    sender.add_periodic_task(10*60, check_for_new_screenshots.s(), name='Check for new screenshots every 10 minutes')
