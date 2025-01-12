from ugs.models.db import db

class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.String)
    following_id = db.Column(db.String)
    __table_args__ = (
        db.ForeignKeyConstraint(['follower_id'], ['foreign_actor.ap_id']),
        db.ForeignKeyConstraint(['following_id'], ['actor.ugs_id']),
    )
    __tablename__ = 'followers'