import json
import os

import streamlit as st
from PIL import Image
from google.genai import Client, types
from pydantic import BaseModel

POSITIVE_OPTION = "I like ❤️"
NEGATIVE_OPTION = "I don't like ❌"


class Answer(BaseModel):
    content: str


api_key = os.environ["GEMINI_API_KEY"]
client = Client(api_key=api_key)


def generate_content(image, length, social_media, mood, language):
    if language == "English":
        if mood == POSITIVE_OPTION:
            mood = "positive"
        else:
            mood = "negative"
        if length == "Medium":
            length = "medium-length"
        prompt = (f"Generate a {length.lower()} {mood} {social_media} (social media) post for this image. Generate the "
                  f"post directly in the `content` field of a json, don't generate anything else.")
    else:
        if "mood" == POSITIVE_OPTION:
            mood = "positif"
        else:
            mood = "négatif"
        if length == "Short":
            prompt = (f"Génère un court poste {social_media} (réseau social) {mood} pour cette image en français. "
                      f"Génère le poste directement dans le champ `content` d'un json, ne génère rien d'autre.")
        elif length == "Medium":
            prompt = (f"Génère un poste {social_media} (réseau social) de taille moyenne {mood} pour cette image en "
                      f"français. Génère le poste directement dans le champ `content` d'un json, ne génère rien "
                      f"d'autre.")
        else:
            prompt = (f"Génère un long poste {social_media} (réseau social) {mood} pour cette image en français. "
                      f"Génère le poste directement dans le champ `content` d'un json, ne génère rien d'autre.")

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=[prompt, image], config=types.GenerateContentConfig(
            temperature=0.5,
            response_mime_type="application/json",
            response_schema=Answer,
        )
    )

    return json.loads(response.text)["content"]


st.set_page_config(page_title="Social Media Post Generator", page_icon="📝")
st.title("📝 Social Media Post Generator")
st.write("Upload any image and let the AI generate a post!")
image = st.file_uploader("Upload an image:", type=["png", "jpg"], label_visibility="collapsed")
length = st.radio("Post length:", options=["Short", "Medium", "Long"], index=1, horizontal=True)
mood = st.radio("Pick a mood:", options=[POSITIVE_OPTION, NEGATIVE_OPTION], index=0, horizontal=True)
language = st.selectbox("Generated content language:", ["English", "French"], index=0)
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
        st.code(result, language="markdown", wrap_lines=True)
        st.image(image)

st.write("❤️ Made by [@tschillaciML](https://x.com/tschillaciML) using Gemini.")
