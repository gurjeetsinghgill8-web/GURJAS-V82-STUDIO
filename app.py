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

st.title("🎬 GURJAS CINEMATIC (FINAL FIXED)")

topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("Generate Cinematic Video")

# =====================
# STORY
# =====================
def generate_story(topic):
    prompt = f"""
    Write a short emotional Hindi story.
    Topic: {topic}
    No headings. Natural storytelling.
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
# VOICE (FIXED)
# =====================
async def generate_voice(text, output):

    chunks = [text[i:i+300] for i in range(0, len(text), 300)]

    voices = [
        "hi-IN-MadhurNeural",
        "hi-IN-SwaraNeural",
        "en-IN-PrabhatNeural"
    ]

    for voice in voices:
        try:
            with open(output, "wb") as f:
                for chunk in chunks:
                    tts = edge_tts.Communicate(chunk, voice, rate="+10%")
                    async for data in tts.stream():
                        if data["type"] == "audio":
                            f.write(data["data"])
            return True
        except:
            continue

    return False

# =====================
# VIDEO
# =====================
def make_video(images, audio, out):

    clip = ImageSequenceClip(images, fps=0.7)

    if os.path.exists(audio):
        audio_clip = AudioFileClip(audio)
        clip = clip.set_audio(audio_clip)

    clip.write_videofile(out, fps=24)

# =====================
# MAIN
# =====================
if btn:

    os.makedirs("out", exist_ok=True)

    st.write("🧠 Generating story...")
    story = generate_story(topic)
    st.text_area("Story", story, height=200)

    # 🎬 CINEMATIC SCENES
    scenes = [
        "middle age indian man holding chest in office, heart attack warning",
        "man collapsing, dramatic lighting, hospital emergency",
        "doctor treating patient in ICU, emotional scene",
        "family crying in hospital, emotional tension",
        "man recovering smiling with family, hope"
    ]

    st.write("🎨 Generating cinematic images...")
    images = []

    for i, scene in enumerate(scenes):
        path = f"out/{i}.png"

        prompt = f"""
        ultra realistic indian cinematic scene,
        {scene},
        35mm film look,
        dramatic lighting,
        real human face,
        not cartoon
        """

        img = generate_image(prompt, path)

        if not img:
            img = Image.new("RGB", (720,1280), (10,10,10))
            img.save(path)

        images.append(path)

    st.write("🔊 Generating voice...")
    audio = "out/audio.mp3"
    ok = asyncio.run(generate_voice(story, audio))

    if not ok:
        st.error("Voice failed")
        st.stop()

    st.write("🎬 Creating cinematic video...")
    video = "out/video.mp4"

    make_video(images, audio, video)

    if os.path.exists(video):
        st.success("✅ Done")
        st.video(video)
    else:
        st.error("Video failed")
