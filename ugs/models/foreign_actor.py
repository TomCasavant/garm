from ugs.models.db import db


class ForeignActor(db.Model):
    ap_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    preferred_username = db.Column(db.String)
    inbox = db.Column(db.String)
    public_key = db.Column(db.String)
    __tablename__ = 'foreign_actor'