"""
ASSA Event Manager — Application Entry Point
Run with: python app.py
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("[OK] ASSA Database tables created / verified!")
        print("[*]  Starting ASSA Event Manager...")
        print("[>>] Visit: http://127.0.0.1:5000")

    app.run(debug=os.getenv('FLASK_DEBUG', '0') == '1', host='127.0.0.1', port=5000)
