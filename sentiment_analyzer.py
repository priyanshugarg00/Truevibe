from textblob import TextBlob
import re

def clean_text(text):
    """
    Clean the input text by removing URLs, special characters, etc.
    """
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove user mentions
    text = re.sub(r'@\w+', '', text)
    # Remove hashtags (keeping the text after #)
    text = re.sub(r'#(\w+)', r'\1', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def analyze_text_sentiment(text):
    """
    Analyze the sentiment of the given text using TextBlob.
    
    Returns:
        dict: Dictionary containing polarity and subjectivity scores
    """
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Create a TextBlob object
    blob = TextBlob(cleaned_text)
    
    # Get sentiment polarity and subjectivity
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    return {
        "polarity": polarity,
        "subjectivity": subjectivity
    }

def get_sentiment_category(polarity):
    """
    Categorize sentiment based on polarity score.
    
    Args:
        polarity (float): The polarity score
        
    Returns:
        str: Sentiment category (Positive, Negative, or Neutral)
    """
    if polarity > 0.05:
        return "Positive"
    elif polarity < -0.05:
        return "Negative"
    else:
        return "Neutral"
