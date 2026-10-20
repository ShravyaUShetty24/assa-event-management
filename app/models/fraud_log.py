"""
ASSA — Fraud Log Model
"""

from datetime import datetime
from app import db


class FraudLog(db.Model):
    __tablename__ = 'fraud_logs'

    log_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid        = db.Column(db.String(36), db.ForeignKey('users.uid', 
                            ondelete='SET NULL'), nullable=True)
    event_id   = db.Column(db.Integer, nullable=True)
    reason     = db.Column(db.String(200), nullable=False)
    score      = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'log_id':     self.log_id,
            'uid':        self.uid,
            'event_id':   self.event_id,
            'reason':     self.reason,
            'score':      self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
