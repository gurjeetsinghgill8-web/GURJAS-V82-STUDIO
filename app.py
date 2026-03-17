import streamlit as st
import os
import requests
import asyncio
import subprocess
import edge_tts
from PIL import Image

# =====================
# API KEYS (Streamlit Secrets)
# =====================
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

st.set_page_config(layout="wide")
st.title("🎬 GURJAS PRO MAX — CINEMATIC ENGINE")

topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("Generate Cinematic Video")

# =====================
# STORY GENERATION
# =====================
def generate_story(topic):
    prompt = f"""
    Write a HIGHLY CINEMATIC Hindi short story (60 sec).
    Topic: {topic}

    Structure:
    - Hook (first 3 sec shocking)
    - Emotional patient case
    - Suspense build
    - Twist
    - Strong CTA

    Keep natural storytelling (NO labels like scene1 etc)
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
# SPLIT INTO SCENES
# =====================
def split_scenes(text):
    parts = text.split(".")
    scenes = [p.strip() for p in parts if len(p.strip()) > 25]
    return scenes[:5]

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
# FALLBACK IMAGE (NO BLANK SCREEN)
# =====================
def fallback(path):
    img = Image.new("RGB", (720,1280), (20,20,20))
    img.save(path)
    return path

# =====================
# VOICE GENERATION
# =====================
async def generate_voice(text, output):
    tts = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+15%")
    await tts.save(output)

# =====================
# CINEMATIC VIDEO ENGINE (FFMPEG)
# =====================
def make_video(images, audio, output):

    if len(images) == 0:
        st.error("❌ No images generated")
        return

    # create list file
    with open("files.txt", "w") as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write("duration 3\n")
        f.write(f"file '{images[-1]}'\n")

    # STEP 1: images → cinematic video
    subprocess.run([
        "ffmpeg","-y",
        "-f","concat",
        "-safe","0",
        "-i","files.txt",
        "-vf","zoompan=z='min(zoom+0.0015,1.2)':d=75",
        "-pix_fmt","yuv420p",
        "temp.mp4"
    ])

    # STEP 2: merge audio
    subprocess.run([
        "ffmpeg","-y",
        "-i","temp.mp4",
        "-i",audio,
        "-c:v","copy",
        "-c:a","aac",
        "-shortest",
        output
    ])

# =====================
# MAIN EXECUTION
# =====================
if btn:

    os.makedirs("out", exist_ok=True)

    st.write("🧠 Generating story...")
    story = generate_story(topic)
    st.text_area("Story", story, height=200)

    scenes = split_scenes(story)

    st.write("🎨 Generating images...")
    images = []

    for i, scene in enumerate(scenes):
        path = f"out/{i}.png"

        prompt = f"""
        Indian hospital cinematic scene,
        emotional lighting,
        realistic human characters,
        4k cinematic,
        {scene}
        """

        img = generate_image(prompt, path)

        if not img:
            img = fallback(path)

        images.append(path)

    st.write("🔊 Generating voice...")
    audio_path = "out/audio.mp3"
    asyncio.run(generate_voice(story, audio_path))

    st.write("🎬 Rendering cinematic video...")
    video_path = "out/final.mp4"

    make_video(images, audio_path, video_path)

    st.success("✅ Done!")
    st.video(video_path)
