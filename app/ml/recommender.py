"""
ASSA — Event Recommendation System
Uses content-based filtering (category similarity) with collaborative
filtering upgrade when enough booking history exists.
Deep Learning version uses a PyTorch embedding model (see train/).
"""

import os
import pickle
from typing import List


_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'ml_models', 'recommender.pkl'
)


class EventRecommender:
    """
    Recommend events to a logged-in user.

    Strategy:
      1. If user has booking history → content-based (same categories)
         + collaborative (users with similar tastes) using cosine similarity.
      2. Cold-start (no history) → return popular upcoming events.
    """

    def __init__(self):
        self._matrix  = None   # user × event matrix for collaborative filtering
        self._user_index: dict = {}
        self._event_ids: list  = []
        self._load_model()

    # ── Model persistence ────────────────────────────────────────────────
    def _load_model(self) -> None:
        if os.path.exists(_MODEL_PATH):
            try:
                with open(_MODEL_PATH, 'rb') as f:
                    data = pickle.load(f)
                self._matrix     = data.get('matrix')
                self._user_index = data.get('user_index', {})
                self._event_ids  = data.get('event_ids', [])
                print('✅ [ML] Recommender model loaded')
            except Exception as exc:
                print(f'⚠️  [ML] Could not load recommender: {exc}')

    def _save_model(self) -> None:
        os.makedirs(os.path.dirname(_MODEL_PATH), exist_ok=True)
        with open(_MODEL_PATH, 'wb') as f:
            pickle.dump({
                'matrix':     self._matrix,
                'user_index': self._user_index,
                'event_ids':  self._event_ids,
            }, f)

    # ── Training ─────────────────────────────────────────────────────────
    def train(self, bookings_df) -> None:
        """
        Train from a pandas DataFrame with columns: uid, event_id.
        Call this manually or via app/ml/train/train_recommender.py.
        """
        import numpy as np
        from sklearn.preprocessing import MultiLabelBinarizer

        grouped = bookings_df.groupby('uid')['event_id'].apply(list)
        mlb     = MultiLabelBinarizer()
        matrix  = mlb.fit_transform(grouped.values)

        self._matrix     = matrix.astype(float)
        self._event_ids  = list(mlb.classes_)
        self._user_index = {uid: i for i, uid in enumerate(grouped.index)}
        self._save_model()
        print(f'✅ [ML] Recommender trained. '
              f'{len(self._user_index)} users, {len(self._event_ids)} events.')

    # ── Inference ────────────────────────────────────────────────────────
    def recommend(self, user_id: str, n: int = 5) -> List[int]:
        """Return up to n recommended event_ids for a given user."""
        try:
            from app.models.booking import Booking
            from app.models.event import Event

            user_bookings   = Booking.query.filter_by(uid=user_id).all()
            booked_event_ids = [b.event_id for b in user_bookings]

            if not booked_event_ids:
                # Cold start: popular upcoming events
                events = Event.query.order_by(Event.date.asc()).limit(n).all()
                return [e.event_id for e in events]

            # Content-based: events in the same categories
            booked_categories = set()
            for b in user_bookings:
                ev = Event.query.get(b.event_id)
                if ev:
                    booked_categories.add(ev.category)

            similar = Event.query.filter(
                Event.category.in_(booked_categories),
                ~Event.event_id.in_(booked_event_ids),
            ).order_by(Event.date.asc()).limit(n).all()

            # Collaborative boost using matrix if available
            if self._matrix is not None and user_id in self._user_index:
                collab_ids = self._collab_filter(user_id, booked_event_ids, n)
                # Merge: prefer collab, fill with content-based
                result = list(dict.fromkeys(collab_ids + [e.event_id for e in similar]))
                return result[:n]

            result = [e.event_id for e in similar]
            if len(result) < n:
                extra = Event.query.filter(
                    ~Event.event_id.in_(booked_event_ids + result)
                ).limit(n - len(result)).all()
                result += [e.event_id for e in extra]

            return result[:n]

        except Exception as exc:
            print(f'⚠️  [ML] Recommender error: {exc}')
            return []

    def _collab_filter(self, user_id: str, booked_ids: list, n: int) -> List[int]:
        """Return event IDs recommended via collaborative filtering."""
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        idx = self._user_index[user_id]
        sims = cosine_similarity(
            self._matrix[idx].reshape(1, -1), self._matrix
        )[0]
        # Top 5 similar users (excluding self)
        top_users = np.argsort(sims)[::-1][1:6]
        candidate_scores: dict = {}
        for u_idx in top_users:
            for e_idx, val in enumerate(self._matrix[u_idx]):
                if val > 0 and self._event_ids[e_idx] not in booked_ids:
                    event_id = self._event_ids[e_idx]
                    candidate_scores[event_id] = candidate_scores.get(event_id, 0) + sims[u_idx]
        ranked = sorted(candidate_scores, key=candidate_scores.get, reverse=True)
        return ranked[:n]
