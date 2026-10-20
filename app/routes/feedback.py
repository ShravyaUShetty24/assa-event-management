"""
ASSA — Feedback Routes
POST /api/feedback/          Submit feedback
GET  /api/feedback/<event_id> Get feedback for an event
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.feedback import Feedback
from app.models.booking import Booking
from app.ml.sentiment import SentimentAnalyzer
from app.ml.fraud_detector import FraudDetector

feedback_bp  = Blueprint('feedback', __name__)
_sentiment   = SentimentAnalyzer()
_fraud_det   = FraudDetector()


@feedback_bp.route('/', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    event_id   = data.get('event_id')
    booking_id = data.get('booking_id')
    rating     = data.get('rating')
    comment    = data.get('comment', '').strip()

    if not event_id or rating is None:
        return jsonify({'error': 'event_id and rating are required'}), 400

    try:
        rating = int(rating)
    except (ValueError, TypeError):
        return jsonify({'error': 'Rating must be an integer'}), 400

    if not (1 <= rating <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    # Must have booked the event
    booking = Booking.query.filter_by(uid=current_user.uid, event_id=event_id).first()
    if not booking:
        return jsonify({'error': 'You must book an event before submitting feedback'}), 403

    # Use the provided booking_id if available, otherwise use the one found
    if not booking_id:
        booking_id = booking.booking_id

    # Duplicate check (one feedback per booking if possible, or per user-event)
    # The requirement says "Save feedback linked to: User, Event, Ticket ID"
    # If we want multiple feedbacks per event but one per ticket, we check by booking_id
    if Feedback.query.filter_by(uid=current_user.uid, booking_id=booking_id).first():
        return jsonify({'error': 'You have already reviewed this ticket'}), 409

    # ML: Sentiment analysis
    sentiment = _sentiment.analyze(comment) if comment else 'neutral'

    # ML: Spam detection
    is_spam = _fraud_det.is_spam_feedback(comment, rating, current_user.uid)

    fb = Feedback(
        uid=current_user.uid,
        event_id=int(event_id),
        booking_id=booking_id,
        rating=rating,
        comment=comment,
        sentiment=sentiment,
        is_spam=is_spam,
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({
        'message':  'Feedback submitted successfully',
        'feedback': fb.to_dict(),
    }), 201


@feedback_bp.route('/<int:event_id>', methods=['GET'])
def get_event_feedback(event_id: int):
    feedbacks = Feedback.query.filter_by(
        event_id=event_id, is_spam=False
    ).order_by(Feedback.created_at.desc()).all()

    avg_rating = round(
        sum(f.rating for f in feedbacks) / len(feedbacks), 2
    ) if feedbacks else 0.0

    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
    for f in feedbacks:
        key = f.sentiment if f.sentiment in sentiment_counts else 'neutral'
        sentiment_counts[key] += 1

    return jsonify({
        'feedbacks':        [f.to_dict() for f in feedbacks],
        'avg_rating':       avg_rating,
        'total_reviews':    len(feedbacks),
        'sentiment_summary': sentiment_counts,
    }), 200
