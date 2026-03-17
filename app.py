import streamlit as st
import os
import requests
import asyncio

# SAFE moviepy imports
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

import edge_tts

# ==============================
# CONFIG
# ==============================
STABILITY_API_KEY = "sk-zO5hqr9zjKHhFwJLrJpiFIlT91ERpzzQGMcf0YzbdOSUmwYx"

st.set_page_config(page_title="GURJAS AI Studio", layout="wide")
st.title("🎬 GURJAS AI VIDEO GENERATOR")

# ==============================
# INPUT
# ==============================
topic = st.text_input("Enter Topic", "Heart Attack Warning")
num_scenes = st.slider("Number of Scenes", 3, 5, 3)

generate_btn = st.button("🚀 Generate Video")

# ==============================
# FUNCTIONS
# ==============================

def generate_ai_image(prompt, output_path):
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*"
    }

    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
    }

    try:
        response = requests.post(url, headers=headers, files=files, timeout=60)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        else:
            st.warning("⚠️ Image API failed, using fallback image")
            return None
    except:
        st.warning("⚠️ API error, using fallback")
        return None


def build_prompt(topic, i):
    return f"""
    Ultra realistic medical scene about {topic},
    Indian doctor explaining to patient,
    hospital environment,
    cinematic lighting, 4k, realistic,
    no cartoon, no illustration
    """


# fallback simple image (so app kabhi crash na ho)
def create_fallback_image(path, text):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (720, 1280), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)
    draw.text((50, 600), text, fill=(255, 255, 255))

    img.save(path)
    return path


async def generate_voice(text, output_file):
    communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural")
    await communicate.save(output_file)


def create_video(images, audio_file, output_file):
    clips = []

    for img in images:
        clip = ImageClip(img).set_duration(3)
        clips.append(clip)

    video = concatenate_videoclips(clips)

    if os.path.exists(audio_file):
        audio = AudioFileClip(audio_file)
        video = video.set_audio(audio)

    video.write_videofile(output_file, fps=24)


# ==============================
# MAIN
# ==============================

if generate_btn:

    os.makedirs("output", exist_ok=True)

    st.write("🖼️ Generating images...")

    images = []

    for i in range(num_scenes):
        path = f"output/scene_{i}.png"

        prompt = build_prompt(topic, i)
        img = generate_ai_image(prompt, path)

        # fallback if API fails
        if not img:
            img = create_fallback_image(path, f"{topic} Scene {i+1}")

        images.append(img)

    st.write("🔊 Generating voice...")

    audio_path = "output/voice.mp3"
    asyncio.run(generate_voice(f"This video explains {topic}", audio_path))

    st.write("🎥 Creating video...")

    video_path = "output/final.mp4"
    create_video(images, audio_path, video_path)

    st.success("✅ Video Ready!")

    st.video(video_path)
