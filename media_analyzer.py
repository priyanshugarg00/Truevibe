import io
import cv2
import numpy as np
import pytesseract
from PIL import Image
import tempfile
import os
import speech_recognition as sr
from sentiment_analyzer import analyze_text_sentiment

def analyze_image(image_bytes):
    """
    Extract text from an image and analyze its sentiment.
    
    Args:
        image_bytes (bytes): The image bytes
        
    Returns:
        dict: Dictionary containing sentiment analysis results and extracted text
    """
    try:
        # Convert bytes to image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert PIL image to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocess the image for better OCR results
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(binary)
        
        # Clean up extracted text
        extracted_text = extracted_text.strip()
        
        # If no text was extracted, return neutral sentiment
        if not extracted_text:
            return {
                "polarity": 0,
                "subjectivity": 0,
                "text": "No text was detected in the image."
            }
        
        # Analyze sentiment of extracted text
        sentiment = analyze_text_sentiment(extracted_text)
        
        # Add the extracted text to the result
        sentiment["text"] = extracted_text
        
        return sentiment
    
    except Exception as e:
        # Return an error message and neutral sentiment
        return {
            "polarity": 0,
            "subjectivity": 0,
            "text": f"Error analyzing image: {str(e)}"
        }

def analyze_video(video_path):
    """
    Extract frames and audio from a video, analyze them, and return combined sentiment.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        dict: Dictionary containing sentiment analysis results
    """
    try:
        # Create a video capture object
        video = cv2.VideoCapture(video_path)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        
        # Extract frames at intervals
        frame_interval = max(1, int(frame_count / 10))  # Extract up to 10 frames
        frames = []
        
        for i in range(0, frame_count, frame_interval):
            video.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = video.read()
            if ret:
                frames.append(frame)
        
        video.release()
        
        # If no frames were extracted, try to analyze audio
        if not frames:
            return extract_audio_from_video(video_path)
        
        # Analyze each frame for text
        frame_sentiments = []
        extracted_texts = []
        
        for frame in frames:
            # Convert to PIL image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Convert back to bytes for analysis
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Analyze the frame
            result = analyze_image(img_bytes)
            
            # If text was found, add to results
            if result["text"] and result["text"] != "No text was detected in the image.":
                frame_sentiments.append({
                    "polarity": result["polarity"],
                    "subjectivity": result["subjectivity"]
                })
                extracted_texts.append(result["text"])
        
        # If no text was found in frames, try audio analysis
        if not frame_sentiments:
            audio_result = extract_audio_from_video(video_path)
            
            # If audio analysis worked, return that
            if audio_result["text"] and audio_result["text"] != "No speech could be recognized from the audio.":
                return audio_result
            
            # Otherwise, return neutral sentiment
            return {
                "polarity": 0,
                "subjectivity": 0,
                "text": "No text or speech could be detected in the video."
            }
        
        # Calculate average sentiment from frames
        avg_polarity = sum(item["polarity"] for item in frame_sentiments) / len(frame_sentiments)
        avg_subjectivity = sum(item["subjectivity"] for item in frame_sentiments) / len(frame_sentiments)
        
        return {
            "polarity": avg_polarity,
            "subjectivity": avg_subjectivity,
            "text": "\n".join(extracted_texts)
        }
    
    except Exception as e:
        # Return an error message and neutral sentiment
        return {
            "polarity": 0,
            "subjectivity": 0,
            "text": f"Error analyzing video: {str(e)}"
        }

def extract_audio_from_video(video_path):
    """
    Extract audio from a video file and perform speech recognition.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        dict: Dictionary containing sentiment analysis results
    """
    try:
        # Create a temporary WAV file for the audio
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio.close()
        
        # Extract audio using FFmpeg via OpenCV
        # This is a simplified approach - in a production environment, you might use a more robust method
        os.system(f'ffmpeg -i "{video_path}" -q:a 0 -map a "{temp_audio.name}" -y')
        
        # Initialize speech recognizer
        recognizer = sr.Recognizer()
        
        # Open the audio file
        with sr.AudioFile(temp_audio.name) as source:
            # Record the audio
            audio = recognizer.record(source)
            
            # Attempt to recognize speech
            try:
                text = recognizer.recognize_google(audio)
                
                # Clean up the temporary file
                os.unlink(temp_audio.name)
                
                # If speech was recognized, analyze sentiment
                if text:
                    sentiment = analyze_text_sentiment(text)
                    sentiment["text"] = text
                    return sentiment
            
            except sr.UnknownValueError:
                pass
            
            except Exception as e:
                # Clean up and re-raise specific exceptions
                os.unlink(temp_audio.name)
                raise e
        
        # Clean up the temporary file
        os.unlink(temp_audio.name)
        
        # If no speech was recognized, return neutral sentiment
        return {
            "polarity": 0,
            "subjectivity": 0,
            "text": "No speech could be recognized from the audio."
        }
    
    except Exception as e:
        # Make sure to clean up
        if 'temp_audio' in locals() and os.path.exists(temp_audio.name):
            os.unlink(temp_audio.name)
        
        # Return an error message and neutral sentiment
        return {
            "polarity": 0,
            "subjectivity": 0,
            "text": f"Error processing audio: {str(e)}"
        }
