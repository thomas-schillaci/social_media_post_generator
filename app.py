import json
import os

import streamlit as st
from PIL import Image
from google.genai import Client, types
from pydantic import BaseModel

POSITIVE_OPTION = "I like ❤️"
NEGATIVE_OPTION = "I don't like ❌"
ENGLISH_LANGUAGE = "English"
FRENCH_LANGUAGE = "French"
SHORT_LENGTH = "Short"
MEDIUM_LENGTH = "Medium"
LONG_LENGTH = "Long"


class Answer(BaseModel):
    content: str

class FrenchAnswer(BaseModel):
    contenu: str


api_key = os.environ["GEMINI_API_KEY"]
client = Client(api_key=api_key)


def generate_content(image, length, social_media, mood, language):
    if language == ENGLISH_LANGUAGE:
        if mood == POSITIVE_OPTION:
            mood = "positive"
        else:
            mood = "negative"
        if length == MEDIUM_LENGTH:
            length = "medium-length"
        prompt = (f"Generate a {length.lower()} {mood} {social_media} (social media) post for this image. Generate the "
                  f"post directly in the `content` field of a json, don't generate anything else.")
        response_schema=Answer
    else:
        length_mapping = {
            SHORT_LENGTH: "courte",
            MEDIUM_LENGTH: "moyenne",
            LONG_LENGTH: "longue"
        }
        mood_mapping = {
            POSITIVE_OPTION: "positive",
            NEGATIVE_OPTION: "négative"
        }
        prompt = (
            f"Génère une publication {length_mapping[length]} "
            f"et {mood_mapping[mood]} pour {social_media} (réseau social) pour cette image. "
            "La publication doit être rédigée en français. "
            "Génère directement la publication dans le champ `contenu` d'un JSON, "
            "ne génère rien d'autre."
        )
        response_schema=FrenchAnswer

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[prompt, image], config=types.GenerateContentConfig(
            temperature=0.5,
            response_mime_type="application/json",
            response_schema=response_schema,
        )
    )

    res = json.loads(response.text)
    if "content" in res:
        return res["content"]
    return res["contenu"]


st.set_page_config(page_title="Social Media Post Generator", page_icon="📝")
st.title("📝 Social Media Post Generator")
st.write("Upload any image and let the AI generate a post!")
image = st.file_uploader("Upload an image:", type=["png", "jpg"], label_visibility="collapsed")
length = st.radio("Post length:", options=[SHORT_LENGTH, MEDIUM_LENGTH, LONG_LENGTH], index=1, horizontal=True)
mood = st.radio("Pick a mood:", options=[POSITIVE_OPTION, NEGATIVE_OPTION], index=0, horizontal=True)
language = st.selectbox("Generated content language:", [ENGLISH_LANGUAGE, FRENCH_LANGUAGE], index=0)
social_media = st.text_input("Social media name:", placeholder="LinkedIn")
go = st.button("Generate!")

if go:
    if not image:
        st.error("Please upload an image.")
    else:
        if not social_media:
            social_media = "LinkedIn"
        image = Image.open(image)
        with st.spinner("Generating content..."):
            result = generate_content(image, length, social_media, mood, language)
        st.markdown(result)
        st.image(image)

st.write("❤️ Made by [@tschillaciML](https://x.com/tschillaciML) using Gemini.")
