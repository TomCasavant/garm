from ugs.models.db import db

class Actor(db.Model):
    ugs_id = db.Column(db.String, primary_key=True)
    profile_image = db.Column(db.String)
    profile_url = db.Column(db.String)
    name = db.Column(db.String)
    steam_id = db.Column(db.String)
    created_at = db.Column(db.String)
    steam_name = db.Column(db.String)
    public_key = db.Column(db.String)
    private_key = db.Column(db.String)
    __tablename__ = 'actor'