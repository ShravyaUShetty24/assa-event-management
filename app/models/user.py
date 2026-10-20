"""
ASSA — User Model
"""

import uuid
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    uid          = db.Column(db.String(36), primary_key=True,
                             default=lambda: str(uuid.uuid4()))
    name         = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role         = db.Column(db.String(20), nullable=False, default='attendee')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    events   = db.relationship('Event',    backref='organizer', lazy=True,
                               foreign_keys='Event.organizer_uid')
    bookings = db.relationship('Booking',  backref='user',      lazy=True,
                               foreign_keys='Booking.uid')
    feedbacks = db.relationship('Feedback', backref='user',     lazy=True,
                                foreign_keys='Feedback.uid')

    # Flask-Login override to use uid as the id string
    def get_id(self) -> str:
        return self.uid

    def to_dict(self) -> dict:
        return {
            'uid':        self.uid,
            'name':       self.name,
            'email':      self.email,
            'role':       self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f'<User {self.email} [{self.role}]>'
