from ugs.models.db import db

class ForeignActivity(db.Model):
    activity_id = db.Column(db.String, primary_key=True)
    activity_type = db.Column(db.String)
    foreign_actor_id = db.Column(db.String, db.ForeignKey('foreign_actor.ap_id'))
    subject_actor_guid = db.Column(db.String)
    datetime_created = db.Column(db.String)
    raw_activity = db.Column(db.String)
    __tablename__ = 'foreign_activity'