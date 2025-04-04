import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import os
from PIL import Image
import io

from sentiment_analyzer import analyze_text_sentiment

from social_media_scraper import fetch_social_media_content
from media_analyzer import analyze_image, analyze_video
from utils import get_sentiment_emoji, get_sentiment_color

# Helper function to display sentiment results
def display_sentiment_results(result):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment Analysis Results")
        sentiment_label = "Positive" if result["polarity"] > 0 else "Negative" if result["polarity"] < 0 else "Neutral"
        st.markdown(f"**Sentiment:** {sentiment_label} {get_sentiment_emoji(result['polarity'])}")
        st.markdown(f"**Polarity Score:** {result['polarity']:.2f}")
        st.markdown(f"**Subjectivity Score:** {result['subjectivity']:.2f}")
        
        if "text" in result:
            st.subheader("Extracted Text")
            st.write(result["text"])
    
    with col2:
        st.subheader("Visualization")
        # Create a bar chart
        df = pd.DataFrame({
            'Metric': ['Polarity', 'Subjectivity'],
            'Score': [result['polarity'], result['subjectivity']]
        })
        
        fig = px.bar(
            df, 
            x='Metric', 
            y='Score', 
            color='Metric',
            color_discrete_map={
                'Polarity': get_sentiment_color(result['polarity']),
                'Subjectivity': '#FFA500'  # Orange for subjectivity
            },
            range_y=[-1, 1],
            title="Sentiment Scores"
        )
        st.plotly_chart(fig, use_container_width=True)


# Configure the page
st.set_page_config(
    page_title="Social Media Sentiment Analyzer",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("📊 Social Media Sentiment Analyzer")
st.markdown("""
This application helps you analyze the sentiment of social media content.
Select an input method below to get started.
""")

# Create tabs for different analysis methods
tab1, tab2, tab3 = st.tabs(["Text Analysis", "Social Media URL", "Media Upload"])

with tab1:
    st.header("Analyze Text")
    text_input = st.text_area("Enter text to analyze", height=150)
    
    if st.button("Analyze Text", key="analyze_text"):
        if text_input:
            with st.spinner("Analyzing text..."):
                result = analyze_text_sentiment(text_input)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Sentiment Analysis Results")
                    sentiment_label = "Positive" if result["polarity"] > 0 else "Negative" if result["polarity"] < 0 else "Neutral"
                    st.markdown(f"**Sentiment:** {sentiment_label} {get_sentiment_emoji(result['polarity'])}")
                    st.markdown(f"**Polarity Score:** {result['polarity']:.2f}")
                    st.markdown(f"**Subjectivity Score:** {result['subjectivity']:.2f}")
                    
                    # Display the analyzed text
                    st.subheader("Analyzed Text")
                    st.write(text_input)
                
                with col2:
                    st.subheader("Visualization")
                    # Create a bar chart
                    df = pd.DataFrame({
                        'Metric': ['Polarity', 'Subjectivity'],
                        'Score': [result['polarity'], result['subjectivity']]
                    })
                    
                    fig = px.bar(
                        df, 
                        x='Metric', 
                        y='Score', 
                        color='Metric',
                        color_discrete_map={
                            'Polarity': get_sentiment_color(result['polarity']),
                            'Subjectivity': '#FFA500'  # Orange for subjectivity
                        },
                        range_y=[-1, 1],
                        title="Sentiment Scores"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Please enter some text to analyze.")

with tab2:
    st.header("Analyze Social Media Post")
    url_input = st.text_input("Enter a social media post URL (Twitter, Instagram, Facebook, Reddit)")
    platform = st.selectbox(
        "Select platform",
        ["Automatic Detection", "Twitter", "Instagram", "Facebook", "Reddit"]
    )
    
    if st.button("Analyze URL", key="analyze_url"):
        if url_input:
            with st.spinner("Fetching and analyzing content..."):
                try:
                    # Adjust platform if automatic detection is selected
                    selected_platform = platform
                    if platform == "Automatic Detection":
                        if "twitter.com" in url_input or "x.com" in url_input:
                            selected_platform = "Twitter"
                        elif "instagram.com" in url_input:
                            selected_platform = "Instagram"
                        elif "facebook.com" in url_input:
                            selected_platform = "Facebook"
                        elif "reddit.com" in url_input:
                            selected_platform = "Reddit"
                        else:
                            selected_platform = "Unknown"
                    
                    if selected_platform == "Unknown":
                        st.error("Could not detect the social media platform. Please select a platform manually.")
                    else:
                        content = fetch_social_media_content(url_input, selected_platform)
                        
                        if content:
                            # Display the content
                            st.subheader(f"Content from {selected_platform}")
                            st.write(content)
                            
                            # Analyze sentiment
                            result = analyze_text_sentiment(content)
                            
                            # Display results
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("Sentiment Analysis Results")
                                sentiment_label = "Positive" if result["polarity"] > 0 else "Negative" if result["polarity"] < 0 else "Neutral"
                                st.markdown(f"**Sentiment:** {sentiment_label} {get_sentiment_emoji(result['polarity'])}")
                                st.markdown(f"**Polarity Score:** {result['polarity']:.2f}")
                                st.markdown(f"**Subjectivity Score:** {result['subjectivity']:.2f}")
                            
                            with col2:
                                st.subheader("Visualization")
                                # Create a bar chart
                                df = pd.DataFrame({
                                    'Metric': ['Polarity', 'Subjectivity'],
                                    'Score': [result['polarity'], result['subjectivity']]
                                })
                                
                                fig = px.bar(
                                    df, 
                                    x='Metric', 
                                    y='Score', 
                                    color='Metric',
                                    color_discrete_map={
                                        'Polarity': get_sentiment_color(result['polarity']),
                                        'Subjectivity': '#FFA500'  # Orange for subjectivity
                                    },
                                    range_y=[-1, 1],
                                    title="Sentiment Scores"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error(f"Could not fetch content from {selected_platform}. Please check the URL and try again.")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.error("Please enter a social media URL to analyze.")

with tab3:
    st.header("Analyze Uploaded Media")
    st.write("Upload an image or video to analyze its sentiment")
    
    uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "mp4", "mov"])
    
    if uploaded_file is not None:
        # Determine file type
        file_type = uploaded_file.name.split(".")[-1].lower()
        is_image = file_type in ["jpg", "jpeg", "png"]
        is_video = file_type in ["mp4", "mov"]
        
        if is_image:
            # Display the image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Analyze image
            if st.button("Analyze Image", key="analyze_image"):
                with st.spinner("Analyzing image..."):
                    try:
                        # Convert PIL Image to bytes for processing
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format=image.format)
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        result = analyze_image(img_byte_arr)
                        
                        # Display results
                        display_sentiment_results(result)
                    except Exception as e:
                        st.error(f"Error analyzing image: {str(e)}")
        
        elif is_video:
            # Display a placeholder for the video
            st.video(uploaded_file)
            
            # Analyze video
            if st.button("Analyze Video", key="analyze_video"):
                with st.spinner("Analyzing video... This may take a moment."):
                    try:
                        # Save the uploaded video to a temporary file
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}")
                        temp_file.write(uploaded_file.getvalue())
                        temp_file.close()
                        
                        result = analyze_video(temp_file.name)
                        
                        # Clean up the temporary file
                        os.unlink(temp_file.name)
                        
                        # Display results
                        display_sentiment_results(result)
                    except Exception as e:
                        st.error(f"Error analyzing video: {str(e)}")
                        # Ensure temporary file is removed in case of error
                        if 'temp_file' in locals() and os.path.exists(temp_file.name):
                            os.unlink(temp_file.name)
        else:
            st.error("Unsupported file format. Please upload a jpg, jpeg, png, mp4, or mov file.")



# Add a footer with information
st.markdown("---")
st.markdown("""
**About this app:**  
This application uses TextBlob for sentiment analysis, which calculates:
- **Polarity**: A value between -1 (negative) and 1 (positive)
- **Subjectivity**: A value between 0 (objective) and 1 (subjective)

The application can analyze text, social media posts, images (via OCR), and videos (via frame analysis and audio extraction).
""")
