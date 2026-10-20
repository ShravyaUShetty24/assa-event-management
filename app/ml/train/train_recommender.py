"""
ASSA — Train Recommender Model
Run from project root: python -m app.ml.train.train_recommender
"""

import os
import sys
import pandas as pd

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sample_bookings.csv')


def train():
    print('📊 Loading booking data...')
    df = pd.read_csv(DATA_PATH)
    print(f'   {len(df)} records loaded')

    from app.ml.recommender import EventRecommender
    rec = EventRecommender()

    print('🧠 Training recommender model...')
    rec.train(df[['uid', 'event_id']])
    print('✅ Recommender training complete!')


if __name__ == '__main__':
    # Bootstrap Flask app context for imports
    from dotenv import load_dotenv
    load_dotenv()

    from app import create_app, db
    app = create_app()
    with app.app_context():
        train()
