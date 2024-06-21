from transformers import pipeline

# Load the sentiment analysis pipeline using the finbert model, which is a pre-trained model for financial sentiment analysis
sentiment_analysis = pipeline("sentiment-analysis", model="ProsusAI/finbert")


def get_sentiment(text_arr):
    """
    Get the sentiment of a given text using the finbert model

    Args:
    text_arr: str, the text to analyze

    Returns:
    confidence: float, the confidence of the sentiment analysis
    label: str, the sentiment label of the text (positive, negative, neutral)
    """
    # Get the sentiment of the text
    sentiment_results = sentiment_analysis(text_arr)

    return sentiment_results
