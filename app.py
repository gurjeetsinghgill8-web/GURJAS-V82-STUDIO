import streamlit as st
import os
import requests
import asyncio

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

import edge_tts
from PIL import Image, ImageDraw, ImageFont

# =====================
# SECRETS
# =====================
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

st.title("🎬 GURJAS CINEMATIC AI")

topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("Generate")

# =====================
# STORY (NO LABELS)
# =====================
def generate_story(topic):
    prompt = f"""
    Hindi me ek emotional cinematic story likho (60 sec video ke liye).

    Topic: {topic}

    RULES:
    - HOOK, STORY jaise words mat likho
    - continuous movie story ho
    - suspense ho
    - real patient feeling ho
    - engaging ho
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
    lines = text.split(".")
    return [l.strip() for l in lines if len(l.strip()) > 20][:6]

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
# FALLBACK
# =====================
def fallback(path, text):
    img = Image.new("RGB", (720,1280), (0,0,0))
    draw = ImageDraw.Draw(img)
    draw.text((50,600), text[:40], fill=(255,255,255))
    img.save(path)
    return path

# =====================
# BRANDING
# =====================
def add_branding(img_path):
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)

    text = "Dr G S Gill | Heart Clinic | Punjab"

    draw.rectangle([0,1100,720,1280], fill=(0,0,0))
    draw.text((30,1130), text, fill=(255,255,255))

    img.save(img_path)
    return img_path

# =====================
# VOICE (MALE FAST)
# =====================
async def voice(text, out):
    tts = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+20%")
    await tts.save(out)

# =====================
# VIDEO
# =====================
def make_video(images, audio, out):

    clip = ImageSequenceClip(images, fps=0.4)

    if os.path.exists(audio):
        audio_clip = AudioFileClip(audio)
        clip = clip.with_audio(audio_clip)

    clip.write_videofile(out, fps=24)

# =====================
# MAIN
# =====================
if btn:

    os.makedirs("out", exist_ok=True)

    st.write("🧠 Writing story...")
    story = generate_story(topic)
    st.text_area("Story", story, height=200)

    scenes = split_scenes(story)

    st.write("🎨 Generating images...")
    images = []

    for i, s in enumerate(scenes):
        path = f"out/{i}.png"

        prompt = f"realistic indian hospital, {s}, cinematic, emotional"

        img = generate_image(prompt, path)

        if not img:
            img = fallback(path, s)

        img = add_branding(img)

        images.append(img)

    st.write("🔊 Voice...")
    audio = "out/audio.mp3"
    asyncio.run(voice(story, audio))

    st.write("🎬 Making video...")
    video = "out/video.mp4"
    make_video(images, audio, video)

    st.video(video)
