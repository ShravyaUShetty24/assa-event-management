"""
ASSA — Event Routes (CRUD)
GET    /api/events/
GET    /api/events/<id>
POST   /api/events/
PUT    /api/events/<id>
DELETE /api/events/<id>
GET    /api/events/categories
"""

import os
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
from app.models.event import Event

events_bp = Blueprint('events', __name__)


@events_bp.route('/', methods=['GET'])
def get_events():
    """List all events with optional search, category filter, and pagination."""
    page     = request.args.get('page',     1,   type=int)
    per_page = request.args.get('per_page', 12,  type=int)
    category = request.args.get('category', '')
    search   = request.args.get('search',   '')

    query = Event.query

    if category:
        query = query.filter(Event.category.ilike(f'%{category}%'))
    if search:
        query = query.filter(
            db.or_(
                Event.title.ilike(f'%{search}%'),
                Event.description.ilike(f'%{search}%'),
                Event.location.ilike(f'%{search}%'),
            )
        )

    query = query.order_by(Event.date.asc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'events':       [e.to_dict() for e in paginated.items],
        'total':        paginated.total,
        'pages':        paginated.pages,
        'current_page': page,
    }), 200


@events_bp.route('/categories', methods=['GET'])
def get_categories():
    cats = db.session.query(Event.category).distinct().order_by(Event.category).all()
    return jsonify({'categories': [c[0] for c in cats]}), 200


@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id: int):
    event = Event.query.get_or_404(event_id)
    return jsonify({'event': event.to_dict()}), 200


@events_bp.route('/', methods=['POST'])
@login_required
def create_event():
    # Relaxed for testing: allow all logged-in users to create events

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    for field in ('title', 'date', 'location', 'category'):
        if not data.get(field):
            return jsonify({'error': f'"{field}" is required'}), 400

    try:
        event_date = datetime.fromisoformat(data['date'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format. Use ISO 8601: YYYY-MM-DDTHH:MM:SS'}), 400

    event = Event(
        organizer_uid=current_user.uid,
        title=data['title'],
        description=data.get('description', ''),
        date=event_date,
        location=data['location'],
        price=data.get('price', 0.00),
        category=data['category'],
        capacity=data.get('capacity', 100),
        image_url=data.get('image_url'),
        artist=data.get('artist')
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({'message': 'Event created successfully', 'event': event.to_dict()}), 201


@events_bp.route('/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id: int):
    event = Event.query.get_or_404(event_id)

    # Owner or admin only
    if current_user.role != 'admin' and event.organizer_uid != current_user.uid:
        return jsonify({'error': 'You do not have permission to edit this event'}), 403

    data = request.get_json() or {}
    updatable = ('title', 'description', 'location', 'price', 'category', 'capacity', 'image_url', 'artist')
    for field in updatable:
        if field in data:
            setattr(event, field, data[field])

    if 'date' in data:
        try:
            event.date = datetime.fromisoformat(data['date'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid date format'}), 400

    db.session.commit()
    return jsonify({'message': 'Event updated', 'event': event.to_dict()}), 200


@events_bp.route('/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id: int):
    event = Event.query.get_or_404(event_id)

    if current_user.role != 'admin' and event.organizer_uid != current_user.uid:
        return jsonify({'error': 'You do not have permission to delete this event'}), 403

    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'}), 200


@events_bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        # Unique filename to avoid collisions
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        upload_folder = os.path.join('static', 'uploads', 'events')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Return the public URL
        return jsonify({'url': f'/static/uploads/events/{filename}'}), 200
    
    return jsonify({'error': 'Upload failed'}), 500
