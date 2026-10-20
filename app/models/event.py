"""
ASSA — Event Model
"""

from datetime import datetime
from app import db


class Event(db.Model):
    __tablename__ = 'events'

    event_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    organizer_uid = db.Column(db.String(36), db.ForeignKey('users.uid',
                              ondelete='CASCADE'), nullable=False)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    date          = db.Column(db.DateTime, nullable=False)
    location      = db.Column(db.String(300), nullable=False)
    price         = db.Column(db.Numeric(10, 2), default=0.00)
    category      = db.Column(db.String(100), nullable=False)
    capacity      = db.Column(db.Integer, default=100)
    image_url     = db.Column(db.String(500), nullable=True)
    artist        = db.Column(db.String(200), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings  = db.relationship('Booking',  backref='event', lazy=True,
                                foreign_keys='Booking.event_id',
                                cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='event', lazy=True,
                                foreign_keys='Feedback.event_id',
                                cascade='all, delete-orphan')

    @property
    def booked_count(self) -> int:
        return len([b for b in self.bookings
                    if b.status in ('pending', 'paid')])

    @property
    def is_full(self) -> bool:
        return self.booked_count >= self.capacity

    @property
    def avg_rating(self) -> float:
        valid = [f.rating for f in self.feedbacks if not f.is_spam]
        return round(sum(valid) / len(valid), 1) if valid else 0.0

    @property
    def is_user_created(self) -> bool:
        # Predefined events are created by the system admin ID seen in schema.sql
        system_admin_id = 'admin-0000-0000-0000-000000000001'
        return self.organizer_uid != system_admin_id

    def to_dict(self) -> dict:
        return {
            'event_id':      self.event_id,
            'organizer_uid': self.organizer_uid,
            'title':         self.title,
            'description':   self.description,
            'date':          self.date.isoformat() if self.date else None,
            'location':      self.location,
            'price':         float(self.price),
            'category':      self.category,
            'capacity':      self.capacity,
            'image_url':     self.image_url,
            'artist':        self.artist,
            'booked_count':  self.booked_count,
            'is_full':       self.is_full,
            'avg_rating':    self.avg_rating,
            'is_user_created': self.is_user_created,
            'created_at':    self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f'<Event #{self.event_id} "{self.title}">'
