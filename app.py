import streamlit as st
import os
import requests
import asyncio

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

import edge_tts
from PIL import Image

# =====================
# KEYS
# =====================
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

st.title("🎬 GURJAS PRO MAX (STABLE)")

topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("Generate")

# =====================
# STORY
# =====================
def generate_story(topic):

    prompt = f"""
    Write a 60 sec Hindi emotional story.
    Topic: {topic}
    cinematic + suspense + realistic
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
    return [p.strip() for p in parts if len(p.strip()) > 20][:6]

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
    img = Image.new("RGB", (720,1280), (20,20,20))
    img.save(path)
    return path

# =====================
# VOICE
# =====================
async def voice(text, out):
    tts = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+15%")
    await tts.save(out)

# =====================
# VIDEO (SUPER STABLE)
# =====================
def make_video(images, audio, out):

    clip = ImageSequenceClip(images, fps=1)

    if os.path.exists(audio):
        audio_clip = AudioFileClip(audio)
        try:
            clip = clip.set_audio(audio_clip)
        except:
            pass

    clip.write_videofile(out, fps=24)

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
        indian hospital scene,
        doctor and patient,
        emotional moment,
        cinematic lighting,
        {s}
        """

        img = generate_image(prompt, path)

        if not img:
            img = fallback(path)

        images.append(img)

    st.write("🔊 Voice...")
    audio = "out/audio.mp3"
    asyncio.run(voice(story, audio))

    st.write("🎬 Rendering...")
    video = "out/final.mp4"

    make_video(images, audio, video)

    st.video(video)
