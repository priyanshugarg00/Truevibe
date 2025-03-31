import requests
import re
import trafilatura
from urllib.parse import urlparse
import streamlit as st

def fetch_social_media_content(url, platform):
    """
    Fetch content from a social media platform based on the URL.
    
    Args:
        url (str): The URL of the social media post
        platform (str): The name of the platform (Twitter, Instagram, Facebook, Reddit)
        
    Returns:
        str: The text content of the post
    """
    if platform == "Twitter":
        return fetch_twitter_content(url)
    elif platform == "Instagram":
        return fetch_instagram_content(url)
    elif platform == "Facebook":
        return fetch_facebook_content(url)
    elif platform == "Reddit":
        return fetch_reddit_content(url)
    else:
        return None

def fetch_twitter_content(url):
    """
    Extract content from a Twitter post.
    Note: This is a simple approach using web scraping.
    
    Args:
        url (str): The URL of the Twitter post
        
    Returns:
        str: The text content of the tweet
    """
    try:
        # Use trafilatura to extract the main content
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded:
            content = trafilatura.extract(downloaded)
            
            # Since Twitter might have limited access due to authentication,
            # we'll extract relevant text from what we can get
            if content:
                # Try to find the tweet text using a simple pattern
                # This is a basic approach and might need refinement
                tweet_pattern = r'(@\w+):\s*(.*?)(?=\n|\Z)'
                matches = re.findall(tweet_pattern, content)
                
                if matches:
                    return "\n".join([f"{username}: {tweet}" for username, tweet in matches])
                
                # If we couldn't extract using the pattern, return the whole content
                return content
            
        st.warning("Limited Twitter content was extracted. For better results, consider using the Twitter API.")
        return "Could not extract complete content from Twitter. Try pasting the tweet text directly."
    
    except Exception as e:
        st.error(f"Error fetching Twitter content: {str(e)}")
        return None

def fetch_instagram_content(url):
    """
    Extract content from an Instagram post.
    Note: This is a simple approach using web scraping.
    
    Args:
        url (str): The URL of the Instagram post
        
    Returns:
        str: The text content of the post
    """
    try:
        # Use trafilatura to extract the main content
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded:
            content = trafilatura.extract(downloaded)
            
            if content:
                # Try to extract the Instagram caption using a simple pattern
                caption_pattern = r'Caption:?\s*(.*?)(?=\n|\Z)'
                match = re.search(caption_pattern, content, re.DOTALL)
                
                if match:
                    return match.group(1).strip()
                
                # If we couldn't extract using the pattern, return the whole content
                return content
        
        st.warning("Limited Instagram content was extracted. For better results, consider using the Instagram API.")
        return "Could not extract complete content from Instagram. Try pasting the post text directly."
    
    except Exception as e:
        st.error(f"Error fetching Instagram content: {str(e)}")
        return None

def fetch_facebook_content(url):
    """
    Extract content from a Facebook post.
    Note: This is a simple approach using web scraping.
    
    Args:
        url (str): The URL of the Facebook post
        
    Returns:
        str: The text content of the post
    """
    try:
        # Use trafilatura to extract the main content
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded:
            content = trafilatura.extract(downloaded)
            
            if content:
                return content
        
        st.warning("Limited Facebook content was extracted. For better results, consider using the Facebook API.")
        return "Could not extract complete content from Facebook. Try pasting the post text directly."
    
    except Exception as e:
        st.error(f"Error fetching Facebook content: {str(e)}")
        return None

def fetch_reddit_content(url):
    """
    Extract content from a Reddit post.
    Note: This function uses the Reddit API to get post content.
    
    Args:
        url (str): The URL of the Reddit post
        
    Returns:
        str: The text content of the post
    """
    try:
        # Parse the URL to extract post ID
        parsed_url = urlparse(url)
        
        # Check if it's a Reddit URL
        if "reddit.com" not in parsed_url.netloc:
            return "Not a valid Reddit URL"
        
        # First try using trafilatura
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded:
            content = trafilatura.extract(downloaded)
            
            if content:
                return content
        
        # If trafilatura fails, try to parse the URL to get a JSON response
        # Convert the URL to a .json URL
        if url.endswith('/'):
            json_url = f"{url}.json"
        else:
            json_url = f"{url}/.json"
        
        response = requests.get(
            json_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract post data
            if isinstance(data, list) and len(data) > 0:
                post_data = data[0]['data']['children'][0]['data']
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                
                if selftext:
                    return f"{title}\n\n{selftext}"
                else:
                    return title
        
        st.warning("Limited Reddit content was extracted. For better results, consider using the Reddit API.")
        return "Could not extract complete content from Reddit. Try pasting the post text directly."
    
    except Exception as e:
        st.error(f"Error fetching Reddit content: {str(e)}")
        return None
