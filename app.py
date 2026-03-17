import streamlit as st
import os
import requests
import asyncio

# ✅ FIXED moviepy import (NO editor error)
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

import edge_tts
from PIL import Image, ImageDraw

# =====================
# 🔐 SECRETS
# =====================
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="GURJAS PRO AI", layout="wide")
st.title("🔥 GURJAS PRO — Viral Medical Video Generator")

# =====================
# INPUT
# =====================
topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("🚀 Generate Video")

# =====================
# STORY (HINDI LONG)
# =====================
def generate_story(topic):

    prompt = f"""
    Hindi me 60 second ka viral reel script likho:

    Topic: {topic}

    Format:
    1. HOOK (shock line)
    2. STORY (real patient case)
    3. BUILDUP (symptoms + suspense)
    4. TWIST
    5. WARNING
    6. CTA

    Emotional + engaging + suspenseful
    """

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }

    r = requests.post(url, headers=headers, json=data)

    return r.json()["choices"][0]["message"]["content"]

# =====================
# SCENE SPLIT
# =====================
def split_scenes(text):
    lines = text.split("\n")
    scenes = [l.strip() for l in lines if len(l.strip()) > 20]
    return scenes[:10]

# =====================
# IMAGE GENERATION
# =====================
def generate_image(prompt, path):

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
        r = requests.post(url, headers=headers, files=files, timeout=60)

        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    except:
        pass

    return None

# =====================
# FALLBACK IMAGE
# =====================
def fallback(path, text):
    img = Image.new("RGB", (720, 1280), (30, 30, 40))
    draw = ImageDraw.Draw(img)
    draw.text((40, 600), text[:50], fill=(255,255,255))
    img.save(path)
    return path

# =====================
# VOICE
# =====================
async def voice(text, output):
    tts = edge_tts.Communicate(text, "hi-IN-SwaraNeural")
    await tts.save(output)

# =====================
# VIDEO CREATION (FIXED)
# =====================
def make_video(images, audio, output):

    clip = ImageSequenceClip(images, fps=0.5)  # slow = longer video

    if os.path.exists(audio):
        sound = AudioFileClip(audio)
        clip = clip.set_audio(sound)

    clip.write_videofile(output, fps=24)

# =====================
# MAIN
# =====================
if btn:

    os.makedirs("output", exist_ok=True)

    st.write("🧠 Creating script...")
    story = generate_story(topic)
    st.text_area("Script", story, height=300)

    scenes = split_scenes(story)

    st.write("🖼 Generating scenes...")
    images = []

    for i, s in enumerate(scenes):
        path = f"output/img_{i}.png"

        prompt = f"""
        realistic indian hospital scene,
        {s},
        cinematic lighting, emotional, 4k
        """

        img = generate_image(prompt, path)

        if not img:
            img = fallback(path, s)

        images.append(img)

    st.write("🔊 Voice...")
    audio_path = "output/voice.mp3"
    asyncio.run(voice(story, audio_path))

    st.write("🎬 Video rendering...")
    video_path = "output/final.mp4"

    make_video(images, audio_path, video_path)

    st.success("✅ Done!")
    st.video(video_path)
