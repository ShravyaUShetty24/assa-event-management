"""
ASSA — Mock Payment Routes
POST /api/payments/<booking_id>        Process mock payment
GET  /api/payments/status/<booking_id> Get payment status
"""

import random
import uuid
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.booking import Booking

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/<int:booking_id>', methods=['POST'])
@login_required
def process_payment(booking_id: int):
    booking = Booking.query.get_or_404(booking_id)

    if booking.uid != current_user.uid:
        return jsonify({'error': 'Unauthorized'}), 403

    if booking.status == 'paid':
        return jsonify({'error': 'This booking has already been paid'}), 400

    if booking.status == 'cancelled':
        return jsonify({'error': 'Cannot pay for a cancelled booking'}), 400

    data = request.get_json() or {}
    card_last4 = str(data.get('card_number', '0000'))[-4:]

    # ── Mock payment simulation (95% success rate) ──
    success = random.random() < 0.95

    if success:
        booking.status = 'paid'
        db.session.commit()

        return jsonify({
            'success':        True,
            'message':        'Payment successful! Your ticket is confirmed.',
            'transaction_id': f'TXN-{uuid.uuid4().hex[:12].upper()}',
            'card_last4':     card_last4,
            'booking':        booking.to_dict(),
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Payment declined. Please try a different card.',
        }), 402


@payments_bp.route('/status/<int:booking_id>', methods=['GET'])
@login_required
def payment_status(booking_id: int):
    booking = Booking.query.get_or_404(booking_id)

    if booking.uid != current_user.uid and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'booking_id':  booking_id,
        'status':      booking.status,
        'ticket_code': booking.ticket_code,
    }), 200
