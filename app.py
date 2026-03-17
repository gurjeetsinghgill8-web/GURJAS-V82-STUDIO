import streamlit as st
import os
import requests
import asyncio

# ✅ NEW SAFE IMPORT (NO editor)
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
# STORY
# =====================
def generate_story(topic):

    prompt = f"""
    Hindi me 60 sec ka engaging reel script likho:

    Topic: {topic}

    HOOK
    STORY
    BUILDUP
    TWIST
    WARNING
    CTA

    Emotional + suspenseful
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

    try:
        r = requests.post(url, headers=headers, json=data, timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Story generation failed"

# =====================
# SCENES
# =====================
def split_scenes(text):
    lines = text.split("\n")
    return [l.strip() for l in lines if len(l.strip()) > 15][:8]

# =====================
# IMAGE
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
    img = Image.new("RGB", (720, 1280), (25, 25, 35))
    draw = ImageDraw.Draw(img)
    draw.text((40, 600), text[:40], fill=(255,255,255))
    img.save(path)
    return path

# =====================
# VOICE
# =====================
async def generate_voice(text, output):
    tts = edge_tts.Communicate(text, "hi-IN-SwaraNeural")
    await tts.save(output)

# =====================
# VIDEO
# =====================
def make_video(images, audio, output):

    clip = ImageSequenceClip(images, fps=0.5)

    if os.path.exists(audio):
        audio_clip = AudioFileClip(audio)
        try:
            clip = clip.with_audio(audio_clip)
        except:
            pass

    clip.write_videofile(output, fps=24)

# =====================
# MAIN
# =====================
if btn:

    os.makedirs("output", exist_ok=True)

    st.write("🧠 Generating script...")
    story = generate_story(topic)
    st.text_area("Script", story, height=300)

    scenes = split_scenes(story)

    st.write("🖼 Generating images...")
    images = []

    for i, scene in enumerate(scenes):
        path = f"output/img_{i}.png"

        prompt = f"""
        realistic indian hospital,
        {scene},
        cinematic lighting, emotional
        """

        img = generate_image(prompt, path)

        if not img:
            img = fallback(path, scene)

        images.append(img)

    st.write("🔊 Voice...")
    audio_path = "output/voice.mp3"
    asyncio.run(generate_voice(story, audio_path))

    st.write("🎬 Creating video...")
    video_path = "output/final.mp4"

    make_video(images, audio_path, video_path)

    if os.path.exists(video_path):
        st.success("✅ Done!")
        st.video(video_path)
    else:
        st.error("❌ Failed")
