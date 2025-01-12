import logging
import os

from celery import Celery, Task
from flask import Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from ugs.models.db import db
# import all classes from ugs.models
from ugs.models.actor import Actor
from ugs.models.activity import Activity
from ugs.models.foreign_activity import ForeignActivity
from ugs.models.foreign_actor import ForeignActor
from ugs.models.follower import Follower
from ugs.models.screenshot import Screenshot

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app(test_config=None):
    logging.basicConfig(level=logging.INFO)

    #app = Flask(__name__, instance_relative_config=True)
    #secret_key = os.getenv('SECRET_KEY')
    #app.config.from_mapping(
    #    CELERY=dict(
    #        broker_url='redis://localhost',
    #        result_backend='redis://localhost',
    #        task_ignore_result=True
    #    ),
    #    SECRET_KEY=secret_key,
    #    DATABASE=os.path.join(app.instance_path, 'ugs.sqlite'),
    #)
    #celery_init_app(app)

    # use sqlalchemy for database and create app
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY = dict(
            broker_url='redis://localhost',
            result_backend='redis://localhost',
            task_ignore_result=True
        ),
        SECRET_KEY=os.getenv('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'ugs.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)
    from ugs.models.db import init_app
    init_app(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    #from . import db


    from . import base_route
    app.register_blueprint(base_route.bp)

    from . import profile
    app.register_blueprint(profile.bp)

    from . import webfinger
    app.register_blueprint(webfinger.bp)

    from . import inbox
    app.register_blueprint(inbox.bp)

    from . import activity
    app.register_blueprint(activity.bp)

    return app