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

st.title("🎬 GURJAS SIMPLE PRO (STABLE)")

topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("Generate Video")

# =====================
# STORY
# =====================
def generate_story(topic):

    prompt = f"""
    Write simple Hindi emotional reel script (no labels).
    Topic: {topic}
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
        r = requests.post(url, headers=headers, files=files)

        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    except:
        pass

    return None

# =====================
# VOICE
# =====================
async def voice(text, out):
    tts = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await tts.save(out)

# =====================
# VIDEO (SAFE)
# =====================
def make_video(images, audio, out):

    if len(images) == 0:
        return

    clip = ImageSequenceClip(images, fps=1)

    if os.path.exists(audio):
        audio_clip = AudioFileClip(audio)
        clip = clip.set_audio(audio_clip)

    clip.write_videofile(out, fps=24)

# =====================
# MAIN
# =====================
if btn:

    os.makedirs("out", exist_ok=True)

    st.write("🧠 Script...")
    story = generate_story(topic)
    st.text_area("Script", story, height=200)

    st.write("🖼 Image...")
    img_path = "out/img.png"

    img = generate_image(f"indian hospital cinematic {topic}", img_path)

    if not img:
        img = Image.new("RGB", (720,1280), (0,0,0))
        img.save(img_path)

    images = [img_path] * 5   # repeat for video

    st.write("🔊 Voice...")
    audio = "out/audio.mp3"
    asyncio.run(voice(story, audio))

    st.write("🎬 Video...")
    video = "out/video.mp4"

    make_video(images, audio, video)

    if os.path.exists(video):
        st.video(video)
    else:
        st.error("Video failed")
