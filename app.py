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

st.title("🔥 GURJAS REAL VIDEO ENGINE")

topic = st.text_input("Enter Topic", "Heart Attack Warning")
btn = st.button("Generate")

# =====================
# STORY
# =====================
def generate_story(topic):
    prompt = f"""
    Hindi emotional story, cinematic style.
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
        r = requests.post(url, headers=headers, files=files, timeout=60)
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
async def generate_voice(text, output):
    tts = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await tts.save(output)

# =====================
# VIDEO (REAL FIX)
# =====================
def make_video(images, audio, output):

    # create list file
    with open("files.txt", "w") as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write("duration 3\n")
        f.write(f"file '{images[-1]}'\n")

    # images → video
    subprocess.run([
        "ffmpeg","-y",
        "-f","concat",
        "-safe","0",
        "-i","files.txt",
        "-pix_fmt","yuv420p",
        "temp.mp4"
    ])

    # add audio
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
# MAIN
# =====================
if btn:

    os.makedirs("out", exist_ok=True)

    st.write("🧠 Story...")
    story = generate_story(topic)
    st.text_area("Story", story, height=200)

    st.write("🎨 Images...")
    scenes = [
        "indian man chest pain office",
        "collapse emergency hospital",
        "doctor ICU treatment",
        "family emotional hospital",
        "recovery happy ending"
    ]

    images = []

    for i, s in enumerate(scenes):
        path = f"out/{i}.png"

        prompt = f"""
        ultra realistic indian cinematic scene,
        {s},
        real human,
        dramatic lighting,
        4k
        """

        img = generate_image(prompt, path)

        if not img:
            img = Image.new("RGB", (720,1280), (20,20,20))
            img.save(path)

        images.append(path)

    st.write("🔊 Voice...")
    audio = "out/audio.mp3"
    asyncio.run(generate_voice(story, audio))

    st.write("🎬 Rendering...")
    video = "out/final.mp4"

    make_video(images, audio, video)

    st.video(video)
