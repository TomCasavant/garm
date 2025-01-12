from ugs.models.db import db

class Activity(db.Model):
    guid = db.Column(db.String, primary_key=True)
    actor_guid = db.Column(db.String, db.ForeignKey('actor.ugs_id'))
    activity_type = db.Column(db.String)
    object_guid = db.Column(db.String, db.ForeignKey('activity.guid'))
    activity_json = db.Column(db.String)
    screenshot_id = db.Column(db.String)
    actor = db.Column(db.String)
    object = db.Column(db.String)
    __tablename__ = 'activity'