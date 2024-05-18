import os
import pandas as pd
import streamlit as st
import speech_recognition as sr
from spellchecker import SpellChecker

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        transcription = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        transcription = "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        transcription = f"Could not request results from Google Speech Recognition service; {e}"
    return transcription

def spell_and_phonetic_correction(text, animal_names, spell):
    corrected_text = []
    for word in text.split():
        corrected_word = spell.correction(word) if spell.unknown([word]) else word
        corrected_text.append(corrected_word.lower())
    corrected_phrase = ' '.join(corrected_text)
    
    corrected_soundex = {soundex(word) for word in corrected_text}
    matched_animals = {name for name in animal_names if name in corrected_text}

    return corrected_phrase, matched_animals

def soundex(word):
    codes = {"bfpv": "1", "cgjkqsxz": "2", "dt": "3", "l": "4", "mn": "5", "r": "6"}
    word = word.lower()
    first_letter = word[0]
    rest = ''.join('0' if char in 'aeiouhwy' else next((code for keys, code in codes.items() if char in keys), '') for char in word[1:])
    coded = first_letter + ''.join(sorted(set(rest), key=rest.index))
    return coded.upper()[:4].ljust(4, '0')

# Load animal names
spell = SpellChecker()
try:
    with open("Animal_list.txt", "r") as file:
        animal_names = [line.strip().lower() for line in file.readlines()]
except FileNotFoundError:
    st.error("Animal list file not found.")
    animal_names = []

# Streamlit app
st.title("Audio Transcription App")
st.write("Upload a WAV file to transcribe")

uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

if uploaded_file is not None:
    try:
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        transcription = transcribe_audio(file_path)
        corrected_text, matched_animals = spell_and_phonetic_correction(transcription, animal_names, spell)
        
        st.text_area("Transcription", corrected_text)
        st.text_area("Matched Animals", ', '.join(matched_animals))
        st.write(f"Number of Matched Animals: {len(matched_animals)}")
        
        transcriptions_df = pd.DataFrame([{'Audio File': os.path.basename(file_path), 
                                           'Transcription': transcription, 
                                           'Corrected Transcription': corrected_text, 
                                           'Matched Animals': ', '.join(matched_animals), 
                                           'Number of Matched Animals': len(matched_animals)}])
        transcriptions_df.to_csv("transcriptions.csv", index=False)
        st.success("Transcription completed and saved to CSV.")
        
        os.remove(file_path)  # Clean up the temporary file
    except Exception as e:
        st.error(f"Failed to process the file: {str(e)}")

### Sharing the App with Others

# 1. **Run the Streamlit App Locally**:
#    Save the code above to a Python file, say `app.py`. You can run the Streamlit app locally using the following command:

#    ```bash
#    streamlit run app.py
