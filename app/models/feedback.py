"""
ASSA — Feedback Model
"""

from datetime import datetime
from app import db


class Feedback(db.Model):
    __tablename__ = 'feedback'

    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid         = db.Column(db.String(36), db.ForeignKey('users.uid',
                            ondelete='CASCADE'), nullable=False)
    event_id    = db.Column(db.Integer, db.ForeignKey('events.event_id',
                            ondelete='CASCADE'), nullable=False)
    booking_id  = db.Column(db.Integer, db.ForeignKey('bookings.booking_id',
                            ondelete='CASCADE'), nullable=True) # Linked to specific ticket
    rating      = db.Column(db.Integer, nullable=False)           # 1–5
    comment     = db.Column(db.Text, nullable=True)
    sentiment   = db.Column(db.String(20), default='neutral')     # positive/neutral/negative
    is_spam     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # One review per booking
    __table_args__ = (
        db.UniqueConstraint('uid', 'booking_id', name='uq_user_booking_feedback'),
    )

    def to_dict(self) -> dict:
        return {
            'feedback_id': self.feedback_id,
            'uid':         self.uid,
            'event_id':    self.event_id,
            'booking_id':  self.booking_id,
            'rating':      self.rating,
            'comment':     self.comment,
            'sentiment':   self.sentiment,
            'is_spam':     self.is_spam,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f'<Feedback #{self.feedback_id} rating={self.rating} sentiment={self.sentiment}>'
