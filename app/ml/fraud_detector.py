"""
ASSA — Fraud & Spam Detection
Combines rule-based heuristics with a trained ML classifier.
Works out of the box with rules; improves when ml_models/fraud_model.pkl exists.
"""

import os
import pickle
from datetime import datetime
from typing import Optional


_SPAM_KEYWORDS = {
    'buy now', 'click here', 'free money', 'you won', 'winner',
    'congratulations', 'urgent', 'limited offer', 'act now', 'guaranteed',
    'no risk', 'earn cash', 'work from home', 'make money fast',
}

_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'ml_models', 'fraud_model.pkl'
)


class FraudDetector:
    """
    Detects:
      1. Fraudulent / suspicious bookings  → score_booking()
      2. Spam / fake feedback comments     → is_spam_feedback()
    """

    def __init__(self):
        self._clf = None
        self._load_model()

    def _load_model(self) -> None:
        if os.path.exists(_MODEL_PATH):
            try:
                with open(_MODEL_PATH, 'rb') as f:
                    self._clf = pickle.load(f)
                print('✅ [ML] Fraud detection model loaded')
            except Exception as exc:
                print(f'⚠️  [ML] Could not load fraud model: {exc}')

    # ── Public API ───────────────────────────────────────────────────────
    def score_booking(self, user_booking_count: int,
                      account_created_at: Optional[datetime]) -> float:
        """
        Returns a fraud score 0.0 (clean) → 1.0 (very suspicious).
        Uses ML model if available, otherwise uses rule-based heuristics.
        """
        features = self._extract_booking_features(
            user_booking_count, account_created_at
        )
        if self._clf:
            try:
                prob = self._clf.predict_proba([features])[0][1]
                return float(prob)
            except Exception:
                pass
        return self._rule_score(features)

    def is_spam_feedback(self, comment: str, rating: int, uid: str) -> bool:
        """
        Returns True if the feedback comment is likely spam.
        """
        if not comment:
            return False

        comment_lower = comment.lower()

        # Rule 1: contains known spam keywords
        if any(kw in comment_lower for kw in _SPAM_KEYWORDS):
            return True

        # Rule 2: very short nonsense with extreme rating
        if len(comment.strip()) < 4:
            return True

        # Rule 3: excessive character repetition (aaaaaaa)
        if any(char * 6 in comment_lower
               for char in 'abcdefghijklmnopqrstuvwxyz'):
            return True

        # Rule 4: all-caps gibberish short string
        if comment.isupper() and len(comment) < 10:
            return True

        return False

    # ── Feature engineering ──────────────────────────────────────────────
    @staticmethod
    def _extract_booking_features(booking_count: int,
                                   created_at: Optional[datetime]) -> list:
        account_age_days = 0
        if created_at:
            account_age_days = max((datetime.utcnow() - created_at).days, 0)
        return [booking_count, account_age_days]

    @staticmethod
    def _rule_score(features: list) -> float:
        booking_count, account_age_days = features
        score = 0.0
        if booking_count > 20:
            score += 0.35
        elif booking_count > 10:
            score += 0.15

        if account_age_days == 0 and booking_count > 2:
            score += 0.50
        elif account_age_days < 3 and booking_count > 5:
            score += 0.30
        elif account_age_days < 7 and booking_count > 10:
            score += 0.20

        return min(score, 1.0)

    # ── Training (call from train_fraud.py) ─────────────────────────────
    def train(self, X, y) -> None:
        from sklearn.ensemble import RandomForestClassifier
        self._clf = RandomForestClassifier(
            n_estimators=100, random_state=42, class_weight='balanced'
        )
        self._clf.fit(X, y)
        os.makedirs(os.path.dirname(_MODEL_PATH), exist_ok=True)
        with open(_MODEL_PATH, 'wb') as f:
            pickle.dump(self._clf, f)
        print('✅ [ML] Fraud model trained and saved')
