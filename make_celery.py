import logging
import os

from garm import create_app

flask_app = create_app()
celery_app = flask_app.extensions['celery']
logger = logging.getLogger(__name__)
