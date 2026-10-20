
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Check if column exists first
        db.session.execute(text("ALTER TABLE feedback ADD COLUMN booking_id INTEGER REFERENCES bookings(booking_id)"))
        db.session.commit()
        print("Successfully added booking_id column to feedback table.")
    except Exception as e:
        print(f"Error: {e}")
