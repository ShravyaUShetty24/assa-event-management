"""
ASSA — Sentiment Analysis
Uses HuggingFace DistilBERT (pretrained, no training needed).
Falls back to keyword-based rules if model cannot load.
"""

import os


class SentimentAnalyzer:
    """
    Analyze user feedback text → 'positive' | 'neutral' | 'negative'
    Primary: HuggingFace distilbert-base-uncased-finetuned-sst-2-english
    Fallback: Rule-based keyword matching
    """

    _POSITIVE_WORDS = {
        'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
        'perfect', 'brilliant', 'outstanding', 'superb', 'love', 'loved',
        'enjoyed', 'happy', 'best', 'good', 'nice', 'impressive', 'satisfied',
    }
    _NEGATIVE_WORDS = {
        'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'hated',
        'disappointing', 'disappointed', 'poor', 'boring', 'waste', 'useless',
        'ugly', 'failed', 'broken', 'disaster', 'regret',
    }

    def __init__(self):
        self._pipeline = None
        load_ml = os.environ.get('LOAD_ML_MODELS', '1') == '1'
        if load_ml:
            self._load_model()

    def _load_model(self) -> None:
        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                'sentiment-analysis',
                model='distilbert-base-uncased-finetuned-sst-2-english',
                truncation=True,
                max_length=512,
            )
            print('[OK] [ML] Sentiment model loaded (DistilBERT)')
        except Exception as exc:
            print(f'[WARN] [ML] Could not load sentiment model: {exc}')
            print('   -> Falling back to keyword-based sentiment analysis')
            self._pipeline = None

    def analyze(self, text: str) -> str:
        """Return 'positive', 'neutral', or 'negative'."""
        if not text or not text.strip():
            return 'neutral'

        if self._pipeline:
            return self._dl_analyze(text)
        return self._rule_analyze(text)

    def _dl_analyze(self, text: str) -> str:
        try:
            result = self._pipeline(text[:512])[0]
            label  = result['label']   # 'POSITIVE' or 'NEGATIVE'
            score  = result['score']   # confidence 0..1

            if label == 'POSITIVE' and score >= 0.65:
                return 'positive'
            if label == 'NEGATIVE' and score >= 0.65:
                return 'negative'
            return 'neutral'
        except Exception as exc:
            print(f'[WARN] [ML] Sentiment inference error: {exc}')
            return self._rule_analyze(text)

    def _rule_analyze(self, text: str) -> str:
        words = set(text.lower().split())
        pos = len(words & self._POSITIVE_WORDS)
        neg = len(words & self._NEGATIVE_WORDS)

        if pos > neg:
            return 'positive'
        if neg > pos:
            return 'negative'
        return 'neutral'
