"""
ASSA — Admin Routes (admin-only)
GET  /api/admin/stats
GET  /api/admin/users
PUT  /api/admin/users/<uid>/role
DEL  /api/admin/users/<uid>
GET  /api/admin/events
GET  /api/admin/bookings
"""

from functools import wraps
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.event import Event
from app.models.booking import Booking
from app.models.feedback import Feedback

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator: only allow admin-role users."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def stats():
    return jsonify({
        'stats': {
            'total_users':    User.query.count(),
            'total_events':   Event.query.count(),
            'total_bookings': Booking.query.count(),
            'paid_bookings':  Booking.query.filter_by(status='paid').count(),
            'pending_bookings': Booking.query.filter_by(status='pending').count(),
            'total_feedback': Feedback.query.count(),
            'spam_detected':  Feedback.query.filter_by(is_spam=True).count(),
            'admins':         User.query.filter_by(role='admin').count(),
            'organizers':     User.query.filter_by(role='organizer').count(),
            'attendees':      User.query.filter_by(role='attendee').count(),
        }
    }), 200


@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users], 'total': len(users)}), 200


@admin_bp.route('/users/<uid>/role', methods=['PUT'])
@login_required
@admin_required
def update_role(uid: str):
    user = User.query.get_or_404(uid)
    data = request.get_json() or {}
    new_role = data.get('role')

    if new_role not in ('admin', 'organizer', 'attendee'):
        return jsonify({'error': 'Invalid role. Must be admin, organizer, or attendee'}), 400

    user.role = new_role
    db.session.commit()
    return jsonify({'message': f'Role updated to {new_role}', 'user': user.to_dict()}), 200


@admin_bp.route('/users/<uid>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(uid: str):
    if uid == current_user.uid:
        return jsonify({'error': 'You cannot delete yourself'}), 400

    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {user.email} deleted'}), 200


@admin_bp.route('/events', methods=['GET'])
@login_required
@admin_required
def get_all_events():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return jsonify({'events': [e.to_dict() for e in events], 'total': len(events)}), 200


@admin_bp.route('/bookings', methods=['GET'])
@login_required
@admin_required
def get_all_bookings():
    bookings = Booking.query.order_by(Booking.booked_at.desc()).all()
    result = []
    for b in bookings:
        d = b.to_dict()
        d['event_title'] = b.event.title if b.event else 'N/A'
        d['user_name']   = b.user.name   if b.user   else 'N/A'
        d['user_email']  = b.user.email  if b.user   else 'N/A'
        result.append(d)
    return jsonify({'bookings': result, 'total': len(result)}), 200


@admin_bp.route('/feedback', methods=['GET'])
@login_required
@admin_required
def get_all_feedback():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return jsonify({'feedback': [f.to_dict() for f in feedbacks], 'total': len(feedbacks)}), 200
