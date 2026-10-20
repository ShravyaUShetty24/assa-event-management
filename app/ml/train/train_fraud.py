"""
ASSA — Train Fraud Detection Model
Run from project root: python -m app.ml.train.train_fraud
"""

import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sample_bookings.csv')


def train():
    print('📊 Loading booking data for fraud training...')
    df = pd.read_csv(DATA_PATH)

    # Features: booking_count, account_age_days
    # Label: is_fraud (simulated in sample data)
    if 'is_fraud' not in df.columns:
        print('⚠️  No is_fraud column found — generating synthetic labels...')
        df['is_fraud'] = (
            (df['booking_count'] > 15) | (df['account_age_days'] < 1)
        ).astype(int)

    X = df[['booking_count', 'account_age_days']].values
    y = df['is_fraud'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print('🧠 Training fraud detection model (RandomForest)...')
    from app.ml.fraud_detector import FraudDetector
    det = FraudDetector()
    det.train(X_train, y_train)

    from sklearn.metrics import classification_report
    preds = det._clf.predict(X_test)
    print('\n📈 Evaluation:')
    print(classification_report(y_test, preds, target_names=['Clean', 'Fraud']))
    print('✅ Fraud model training complete!')


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    train()
