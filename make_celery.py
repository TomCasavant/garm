import logging
import os

from garm import create_app
from garm.activity import send_activity
from garm.db import get_db

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

    # Get the activity associated with the screenshot
    #unposted_activity = db.execute(
    #    'SELECT * FROM activity WHERE screenshot_id = ?', (unposted_screenshot['steam_id'])
    #).fetchone()

    unposted_activity = db.execute(
        'SELECT * FROM activity WHERE screenshot_id = ? AND activity_type = ?', (unposted_screenshot['steam_id'], 'Note')
    ).fetchone()

    print(f"Sending activity {unposted_screenshot}")
    send_activity(unposted_activity, db)


# scheudle task for every 10 minutes, share screenshot with followers
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1*60, post_screenshot.s(), name='Post screenshots every 10 minutes')