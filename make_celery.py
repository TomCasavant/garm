import logging
import os

from garm import create_app

flask_app = create_app()
celery_app = flask_app.extensions['celery']
logger = logging.getLogger(__name__)

# Schedule task for every 10 minutes
# Should get the most recent 5 screenshots
# if there are screenshots that are not in the database, add them
# Then send out Create Note to all followers
