import logging
import os

from ugs import create_app
from ugs.activity import send_activity
from ugs.db import get_db
from ugs.models.screenshot import SteamScreenshot
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
    # Gets all the screenshots
    # Finds most recent that doesn't have a CREATE Note in the db
    # Sends out a Create Note to all followers
    db = get_db()
    screenshots = db.execute(
        'SELECT * FROM screenshot ORDER BY time_created ASC'
    ).fetchall()

    unposted_screenshot = None
    for screenshot in screenshots:
        screenshot_id = screenshot['steam_id']
        create_activity = db.execute(
            'SELECT * FROM activity WHERE screenshot_id = ? AND activity_type = ?', (screenshot_id, 'Create')
        ).fetchone()
        if create_activity is None:
            unposted_screenshot = screenshot
            break

    if unposted_screenshot is None:
        return

    unposted_activity = db.execute(
        'SELECT * FROM activity WHERE screenshot_id = ? AND activity_type = ?', (unposted_screenshot['steam_id'], 'Note')
    ).fetchone()

    send_activity(unposted_activity, db)

# Every 15 minutes check if there are new screenshots
@celery_app.task
def check_for_new_screenshots():
    # Get the 10 newest screenshots
    db = get_db()
    api_key = os.getenv('STEAM_API_KEY')
    steam_platform = SteamPlatform(db)
    screenshots = steam_platform.get_screenshots()['response']['publishedfiledetails']
    # Check if the first screenshot is in the database
    newest_screenshot = screenshots[0]
    screenshot_id = newest_screenshot['publishedfileid']
    screenshot_db = db.execute(
        'SELECT * FROM screenshot WHERE steam_id = ?', (screenshot_id,)
    ).fetchone()
    actor = db.execute(
        'SELECT * FROM actor WHERE steam_id = ?', (os.getenv('STEAM_ID'),)
    ).fetchone()
    if screenshot_db is not None:
        return

    # Otherwise, loop through the screenshots until we find one that is in the database
    for screenshot in screenshots:
        screenshot_id = screenshot['publishedfileid']
        screenshot_search = db.execute(
            'SELECT * FROM screenshot WHERE steam_id = ?', (screenshot_id,)
        ).fetchone()
        if screenshot_search is not None:
            break

        # Add the screenshot to the database
        steam_platform.add_screenshot(screenshot, actor['ugs_id'])

        # Get the newly created activity
        # TODO: Can we just return the created activity? So we don't search the database as much
        activity = db.execute(
            'SELECT * FROM activity WHERE screenshot_id = ? AND activity_type = ?', (screenshot_id, 'Note')
        ).fetchone()

        # Send the activity to all followers
        send_activity(activity, db)


# scheudle task for every 10 minutes, share screenshot with followers
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(45*60, post_screenshot.s(), name='Post screenshots every 45 minutes')
    sender.add_periodic_task(10*60, check_for_new_screenshots.s(), name='Check for new screenshots every 10 minutes')
