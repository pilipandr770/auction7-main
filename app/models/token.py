from app import db
from datetime import datetime

class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_address = db.Column(db.String(42), nullable=True)  # Token contract address on blockchain
    amount = db.Column(db.Integer, default=0)  # Amount of tokens owned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('tokens', lazy=True))
    
    def __init__(self, user_id, amount=1, token_address=None):
        self.user_id = user_id
        self.amount = amount
        self.token_address = token_address
