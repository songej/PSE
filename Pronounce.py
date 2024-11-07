import streamlit as st
import requests

# Streamlit interface
st.title("Phonetic Transcription Finder")
st.write("Enter a list of words (one per line) to retrieve their phonetic transcriptions.")

# Input area for words
word_list = st.text_area("Enter words:", height=200).splitlines()

# API key (replace 'YOUR_API_KEY' with your actual key)
API_KEY = 'YOUR_API_KEY'
API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/{}?key={}"

# Function to get phonetic transcription
def get_phonetic(word):
    response = requests.get(API_URL.format(word, API_KEY))
    if response.status_code == 200:
        data = response.json()
        if data and 'hwi' in data[0] and 'prs' in data[0]['hwi']:
            # Return the phonetic transcription if available
            return data[0]['hwi']['prs'][0]['mw']
    return "N/A"  # Return N/A if no transcription found

# Button to trigger the API call
if st.button("Get Phonetic Transcriptions"):
    if word_list:
        # Retrieve and display transcriptions
        transcriptions = {word: get_phonetic(word) for word in word_list}
        
        # Display as a table
        st.write("## Phonetic Transcriptions")
        st.table(list(transcriptions.items()))
    else:
        st.warning("Please enter at least one word.")
