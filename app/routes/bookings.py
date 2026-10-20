"""
ASSA — Booking Routes
POST /api/bookings/<event_id>       Book an event
GET  /api/bookings/my               My bookings
GET  /api/bookings/ticket/<id>      View single ticket
POST /api/bookings/cancel/<id>      Cancel a booking
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.booking import Booking
from app.models.event import Event
from app.ml.fraud_detector import FraudDetector

bookings_bp  = Blueprint('bookings', __name__)
_fraud_det   = FraudDetector()


@bookings_bp.route('/<int:event_id>', methods=['POST'])
@login_required
def book_event(event_id: int):
    event = Event.query.get_or_404(event_id)

    # Duplicate check (already here but good to be sure)
    if Booking.query.filter_by(uid=current_user.uid, event_id=event_id).first():
        return jsonify({'error': 'You have already booked this event'}), 409

    # Fraud check: Rapid bookings
    from datetime import datetime, timedelta
    from app.models.fraud_log import FraudLog
    
    last_booking = Booking.query.filter_by(uid=current_user.uid).order_by(Booking.booked_at.desc()).first()
    if last_booking and (datetime.utcnow() - last_booking.booked_at) < timedelta(seconds=10):
        log = FraudLog(uid=current_user.uid, event_id=event_id, reason='Rapid booking attempt (< 10s)', score=0.9)
        db.session.add(log)
        db.session.commit()
        return jsonify({'error': 'Too many booking attempts. Please wait a moment.'}), 429

    # Fraud scoring
    user_booking_count = Booking.query.filter_by(uid=current_user.uid).count()
    fraud_score = _fraud_det.score_booking(user_booking_count, current_user.created_at)

    if fraud_score > 0.8:
        log = FraudLog(uid=current_user.uid, event_id=event_id, reason='High fraud score detected', score=fraud_score)
        db.session.add(log)
        db.session.commit()
        return jsonify({'error': 'Your account has been flagged for unusual activity. Please contact support.'}), 403

    status = 'paid' if event.price == 0 else 'pending'
    booking = Booking(uid=current_user.uid, event_id=event_id, status=status)
    db.session.add(booking)
    db.session.commit()

    msg = 'Booking confirmed!' if status == 'paid' else 'Booking created! Complete payment to confirm.'
    return jsonify({
        'message':     msg,
        'booking':     booking.to_dict(),
        'fraud_score': round(fraud_score, 3),
    }), 201


@bookings_bp.route('/my', methods=['GET'])
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(uid=current_user.uid).order_by(
        Booking.booked_at.desc()
    ).all()

    result = []
    for b in bookings:
        d = b.to_dict()
        d['event'] = b.event.to_dict() if b.event else None
        result.append(d)

    return jsonify({'bookings': result, 'total': len(result)}), 200


@bookings_bp.route('/ticket/<int:booking_id>', methods=['GET'])
@login_required
def get_ticket(booking_id: int):
    booking = Booking.query.get_or_404(booking_id)

    if booking.uid != current_user.uid and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'ticket': {
            **booking.to_dict(),
            'event': booking.event.to_dict() if booking.event else None,
            'user':  booking.user.to_dict()  if booking.user  else None,
        }
    }), 200


@bookings_bp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id: int):
    booking = Booking.query.get_or_404(booking_id)

    if booking.uid != current_user.uid and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.status == 'cancelled':
        return jsonify({'error': 'Booking is already cancelled'}), 400

    booking.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Booking cancelled', 'booking': booking.to_dict()}), 200
