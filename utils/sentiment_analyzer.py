from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

class SentimentAnalyzer:
    def __init__(self):
        nltk.download("vader_lexicon", quiet=True)
        self.sia = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, text):
        return self.sia.polarity_scores(text)