import streamlit as st
import os
import requests
from moviepy.editor import *
import asyncio
import edge_tts

# ==============================
# CONFIG
# ==============================
STABILITY_API_KEY = "sk-zO5hqr9zjKHhFwJLrJpiFIlT91ERpzzQGMcf0YzbdOSUmwYx"

st.set_page_config(page_title="GURJAS AI Studio", layout="wide")

st.title("🎬 GURJAS AI VIDEO GENERATOR (PRO VERSION)")

# ==============================
# INPUT
# ==============================
topic = st.text_input("Enter Topic (e.g. Heart Attack Warning)")
num_scenes = st.slider("Number of Scenes", 3, 6, 4)

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

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        st.error("Image generation failed")
        return None


def build_prompt(topic, i):
    return f"""
    Ultra realistic medical scene about {topic},
    scene {i},
    Indian doctor, hospital environment,
    cinematic lighting, 4k, realistic, no cartoon
    """


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
# MAIN PIPELINE
# ==============================

if generate_btn and topic:

    os.makedirs("output", exist_ok=True)

    st.write("🖼️ Generating Images...")
    images = []

    for i in range(num_scenes):
        path = f"output/scene_{i}.png"
        prompt = build_prompt(topic, i)

        img = generate_ai_image(prompt, path)
        if img:
            images.append(img)

    st.write("🔊 Generating Voice...")

    audio_path = "output/voice.mp3"
    asyncio.run(generate_voice(f"This video explains {topic}", audio_path))

    st.write("🎥 Creating Video...")

    video_path = "output/final.mp4"
    create_video(images, audio_path, video_path)

    st.success("✅ Done!")

    st.video(video_path)
