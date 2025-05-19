from app import db
from datetime import datetime
from app.models.user import User

class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    votes_for = db.Column(db.Integer, default=0)
    votes_against = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    creator = db.relationship('User', backref='proposals')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'for' or 'against'
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='votes')
    proposal = db.relationship('Proposal', backref='vote_records')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'proposal_id', name='uix_user_proposal'),)
