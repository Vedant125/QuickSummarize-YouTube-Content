import streamlit as st
from dotenv import load_dotenv
load_dotenv()  # Load all environment variables
import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

prompt = """You are Youtube Video Summarizer. You will be taking the transcript text and 
    summarizing the entire video and providing the important summary in points within 250 words.
    Please provide the summary of the text given here: """

# Extracting Transcript data from YouTube
def extract_transcript_details(youtube_video_url, languages=['en', 'hi', 'es', 'fr', 'de']):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = None
        for lang in languages:
            try:
                transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                break
            except (NoTranscriptFound, CouldNotRetrieveTranscript):
                continue

        if not transcript_text:
            raise NoTranscriptFound("No transcript found for the provided languages.")

        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except Exception as e:
        return str(e)

# Getting Summary Based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt + str(transcript_text))
    return response.text

st.title('YouTube Transcript to Detailed Notes Converter')

youtube_link = st.text_input('Enter YouTube Video Link:')

if youtube_link:
    video_id = youtube_link.split('=')[1]
    st.image(f"https://i.ytimg.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button('Get Detailed Notes'):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown('Detailed Notes:')
        st.write(summary)
