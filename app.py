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


def generate_content(image, length, social_media, mood):
    if mood == POSITIVE_OPTION:
        mood = "positive"
    else:
        mood = "negative"
    if length == "Medium":
        length = "medium-length"

    prompt = (f"Generate a {length.lower()} {mood} {social_media} (social media) post for this image. Generate the "
              f"post directly in the `content` field of a json, don't generate anything else.")

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
social_media = st.text_input("Social Media", placeholder="LinkedIn")
mood = st.radio("Pick a mood:", options=[POSITIVE_OPTION, NEGATIVE_OPTION], index=0, horizontal=True)
go = st.button("Generate!")

if go:
    if not image:
        st.error("Please upload an image.")
    else:
        if not social_media:
            social_media = "LinkedIn"
        image = Image.open(image)
        with st.spinner("Generating content..."):
            result = generate_content(image, length, social_media, mood)
            st.markdown(result)

st.write("❤️ Made by [@tschillaciML](https://x.com/tschillaciML) using Gemini.")
