# If you haven't installed these packages yet, uncomment and run in your terminal:
# !pip install googletrans==4.0.0-rc1
# !pip install pillow
# !pip install gtts
# !pip install easyocr
# !pip install streamlit
# !pip install opencv-python

import streamlit as st
import easyocr
import cv2
import numpy as np
from googletrans import Translator
from gtts import gTTS
from io import BytesIO
from PIL import Image
import tempfile
import os

# Initialize EasyOCR (add or remove languages according to your needs)
reader = easyocr.Reader(["en", "hi", "mr"])

# Initialize Translator
translator = Translator()

st.title("Text Detection and Translation App")

# 1) Radio for user input choice
choice = st.radio(
    "Select how you want to provide text:",
    ("Upload Image", "Capture Image", "Enter Text")
)

text_combined = None
img_array = None

# 2) Handle each choice separately
if choice == "Upload Image":
    uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Convert uploaded file to an OpenCV image (NumPy array)
        file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
        img_array = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img_array is not None:
            # Convert BGR (OpenCV default) to RGB for correct rendering in Streamlit
            st.image(img_array[:, :, [2, 1, 0]], caption="Uploaded Image", use_column_width=True)
        else:
            st.error("Failed to convert the uploaded file into an image.")

elif choice == "Capture Image":
    # st.camera_input provides a user-friendly camera interface
    captured_photo = st.camera_input("Capture Image")
    if captured_photo is not None:
        # Convert the captured photo to an OpenCV-compatible NumPy array
        file_bytes = np.frombuffer(captured_photo.getvalue(), np.uint8)
        img_array = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img_array is not None:
            st.image(img_array[:, :, [2, 1, 0]], caption="Captured Image", use_column_width=True)
        else:
            st.error("Failed to convert the captured image into a NumPy array.")

elif choice == "Enter Text":
    user_text = st.text_area("Enter your text here:")
    if user_text:
        st.write("Entered Text:", user_text)
        text_combined = user_text

# 3) Extract text using OCR if an image is present (for Upload or Capture)
if img_array is not None:
    ocr_result = reader.readtext(img_array, detail=0)
    if ocr_result:
        text_combined = " ".join(ocr_result)
        st.write("Extracted Text:", text_combined)
    else:
        st.warning("No text found in the image.")

# 4) Proceed only if text_combined is available (either from image OCR or typed text)
if text_combined:
    # Detect language
    detection_result = translator.detect(text_combined)
    detected_lang = detection_result.lang
    detected_confidence = detection_result.confidence

    if detected_confidence is None:
        st.write(f"Detected Language: {detected_lang} (confidence not available)")
    else:
        st.write(f"Detected Language: {detected_lang} (confidence {detected_confidence:.2f})")

    # Allow user to select translation language
    target_language = st.selectbox(
        "Select the language to translate into:",
        ["Hindi", "Spanish", "French", "Marathi", "Gujarati"]
    )

    lang_map = {
        "Hindi": "hi",
        "Spanish": "es",
        "French": "fr",
        "Marathi": "mr",
        "Gujarati": "gu"
    }

    if st.button("Translate"):
        # Perform the translation
        translated_text = translator.translate(text_combined, src=detected_lang, dest=lang_map[target_language]).text
        st.write("Translated Text:", translated_text)

        # Text-to-Speech
        if st.button("Convert to Speech"):
            st.write("Generating speech... Please wait.")

            # Approach A: Generate Audio In-Memory
            try:
                tts = gTTS(text=translated_text, lang=lang_map[target_language])
                audio_buffer = BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)

                st.audio(audio_buffer, format="audio/mp3")
                st.success("Audio generated succesfully using in-memory approach!")
            except Exception as e:
                st.error(f"Failed to generate in-memory audio. Error: {str(e)}")


            # Approach B: Generate Audio as a Temporary File (Optional fallback)
            # Sometimes writing to an actual file helps debug or ensure playback
            # (Uncomment if you want to test file-based playback)
            #
             #try:
              #   with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
               #      tts.write_to_fp(tmp_file)
                #     tmp_file_path = tmp_file.name
#
 #                audio_file_size = os.path.getsize(tmp_file_path)
  #               st.write(f"Temp audio file size: {audio_file_size} bytes")

                 # Display audio in Streamlit
    #             with open(tmp_file_path, "rb") as f:
   #                  st.audio(f.read(), format="audio/mp3")
            #
     #            st.success("Audio generated successfully using file-based approach!")
            #
                 # Clean up
      #           os.remove(tmp_file_path)
       #      except Exception as ex:
        #         st.error(f"Failed to generate file-based audio. Error: {str(ex)}")
