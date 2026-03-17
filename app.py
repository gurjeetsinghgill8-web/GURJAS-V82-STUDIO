import streamlit as st
import os
import requests
import asyncio

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip

import edge_tts
from PIL import Image

# =====================
# SECRETS
# =====================
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

st.title("🎬 GURJAS PRO MAX (CINEMATIC)")

topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("Generate")

# =====================
# STORY
# =====================
def generate_story(topic):

    prompt = f"""
    Write a cinematic Hindi emotional story (60 sec)

    Topic: {topic}

    No headings. Continuous story.
    suspense + emotional + realistic
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
def fallback(path):
    img = Image.new("RGB", (720,1280), (15,15,15))
    img.save(path)
    return path

# =====================
# VOICE
# =====================
async def voice(text, out):
    tts = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+15%")
    await tts.save(out)

# =====================
# VIDEO (CINEMATIC)
# =====================
def make_video(images, scenes, audio, out):

    clips = []

    for i, img in enumerate(images):

        base = ImageClip(img).set_duration(5)

        # 🎥 zoom effect
        zoom = base.resize(lambda t: 1 + 0.05*t)

        # 📝 subtitle (English safe)
        txt = TextClip(
            scenes[i][:60],
            fontsize=40,
            color='white',
            method='caption',
            size=(700, None)
        ).set_position(("center", "bottom")).set_duration(5)

        video = CompositeVideoClip([zoom, txt])
        clips.append(video)

    final = concatenate_videoclips(clips, method="compose")

    if os.path.exists(audio):
        audio_clip = AudioFileClip(audio)
        final = final.set_audio(audio_clip)

    final.write_videofile(out, fps=24)

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
        ultra realistic indian hospital,
        doctor patient emotional,
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

    make_video(images, scenes, audio, video)

    st.video(video)
