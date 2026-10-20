"""
ASSA Event Manager — Flask Application Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_name: str = None):
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='../static'
    )

    # ── Config ──────────────────────────────────────────
    from .config import config
    env = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config.get(env, config['default']))

    # ── Extensions ──────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'main.login_page'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # ── Blueprints ──────────────────────────────────────
    from .routes.auth import auth_bp
    from .routes.events import events_bp
    from .routes.bookings import bookings_bp
    from .routes.feedback import feedback_bp
    from .routes.payments import payments_bp
    from .routes.admin import admin_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,     url_prefix='/api/auth')
    app.register_blueprint(events_bp,   url_prefix='/api/events')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp,    url_prefix='/api/admin')

    return app
