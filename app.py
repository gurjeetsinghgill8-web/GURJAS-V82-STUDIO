import streamlit as st
import os
import requests
import asyncio
import subprocess

import edge_tts
from PIL import Image

# =====================
# KEYS
# =====================
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

st.title("🎬 GURJAS PRO MAX (NO FREEZE ENGINE)")

topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("Generate")

# =====================
# STORY
# =====================
def generate_story(topic):

    prompt = f"""
    Write a 60 sec Hindi emotional cinematic story.
    Topic: {topic}
    suspense + patient case + emotional
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
# SPLIT
# =====================
def split_scenes(text):
    parts = text.split(".")
    return [p.strip() for p in parts if len(p.strip()) > 20][:5]

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
# FALLBACK
# =====================
def fallback(path):
    img = Image.new("RGB", (720,1280), (30,30,30))
    img.save(path)
    return path

# =====================
# VOICE
# =====================
async def voice(text, out):
    tts = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+10%")
    await tts.save(out)

# =====================
# FFMPEG VIDEO (KEY FIX)
# =====================
def make_video(images, audio, output):

    # create file list
    with open("files.txt", "w") as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write("duration 3\n")

    # last frame repeat
    f.write(f"file '{images[-1]}'\n")

    # STEP 1: images → video
    subprocess.run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "files.txt",
        "-vsync", "vfr",
        "-pix_fmt", "yuv420p",
        "temp.mp4"
    ])

    # STEP 2: add audio
    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", "temp.mp4",
        "-i", audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output
    ])

# =====================
# MAIN
# =====================
if btn:

    os.makedirs("out", exist_ok=True)

    st.write("🧠 Story...")
    story = generate_story(topic)
    st.text_area("Story", story, height=200)

    scenes = split_scenes(story)

    st.write("🎨 Images...")
    images = []

    for i, s in enumerate(scenes):
        path = f"out/{i}.png"

        prompt = f"""
        indian hospital,
        emotional doctor patient,
        cinematic lighting,
        {s}
        """

        img = generate_image(prompt, path)

        if not img:
            img = fallback(path)

        images.append(path)

    st.write("🔊 Voice...")
    audio = "out/audio.mp3"
    asyncio.run(voice(story, audio))

    st.write("🎬 Rendering (FAST)...")
    video = "out/final.mp4"

    make_video(images, audio, video)

    st.video(video)
