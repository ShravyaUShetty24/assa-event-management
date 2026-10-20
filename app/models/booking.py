"""
ASSA — Booking Model
"""

import uuid
from datetime import datetime
from app import db


def _generate_ticket_code() -> str:
    return f"ASSA-{uuid.uuid4().hex[:8].upper()}"


class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid         = db.Column(db.String(36), db.ForeignKey('users.uid',
                            ondelete='CASCADE'), nullable=False)
    event_id    = db.Column(db.Integer, db.ForeignKey('events.event_id',
                            ondelete='CASCADE'), nullable=False)
    status      = db.Column(db.String(20), nullable=False, default='pending')
    booked_at   = db.Column(db.DateTime, default=datetime.utcnow)
    ticket_code = db.Column(db.String(50), unique=True, nullable=False,
                            default=_generate_ticket_code)

    # Unique: one booking per user per event
    __table_args__ = (
        db.UniqueConstraint('uid', 'event_id', name='uq_user_event_booking'),
    )

    def to_dict(self) -> dict:
        return {
            'booking_id':  self.booking_id,
            'uid':         self.uid,
            'event_id':    self.event_id,
            'status':      self.status,
            'booked_at':   self.booked_at.isoformat() if self.booked_at else None,
            'ticket_code': self.ticket_code,
        }

    def __repr__(self) -> str:
        return f'<Booking #{self.booking_id} [{self.status}] {self.ticket_code}>'
