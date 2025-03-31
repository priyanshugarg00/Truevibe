def get_sentiment_emoji(polarity):
    """
    Return an appropriate emoji based on sentiment polarity.
    
    Args:
        polarity (float): Sentiment polarity score
        
    Returns:
        str: Emoji representing the sentiment
    """
    if polarity > 0.5:
        return "😄"  # Very positive
    elif polarity > 0:
        return "🙂"  # Positive
    elif polarity == 0:
        return "😐"  # Neutral
    elif polarity > -0.5:
        return "🙁"  # Negative
    else:
        return "😠"  # Very negative

def get_sentiment_color(polarity):
    """
    Return an appropriate color based on sentiment polarity.
    
    Args:
        polarity (float): Sentiment polarity score
        
    Returns:
        str: Hex color code representing the sentiment
    """
    if polarity > 0.5:
        return '#2ECC71'  # Green - Very positive
    elif polarity > 0:
        return '#82E0AA'  # Light green - Positive
    elif polarity == 0:
        return '#BDC3C7'  # Gray - Neutral
    elif polarity > -0.5:
        return '#F1948A'  # Light red - Negative
    else:
        return '#E74C3C'  # Red - Very negative
