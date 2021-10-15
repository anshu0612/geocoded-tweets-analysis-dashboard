from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_sentiment(doc):
    score = analyzer.polarity_scores(doc)['compound']
    # As per vader's repo : https://github.com/cjhutto/vaderSentiment
    if score >= 0.05:
        sentiment = "positive"
    elif score <= -0.05:

        sentiment = "negative"
    else:
        sentiment = "neutral"
    return sentiment
