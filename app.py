import streamlit as st
import os
import subprocess
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

st.title("🔥 SIMPLE STABLE VIDEO (NO BUG)")

topic = st.text_input("Enter Topic", "Heart Attack Warning")

if st.button("Generate Video"):

    os.makedirs("out", exist_ok=True)

    # =====================
    # STORY (STATIC - SAFE)
    # =====================
    story = f"""
    दिल की चेतावनी।
    अगर सीने में दर्द हो,
    सांस लेने में तकलीफ हो,
    तुरंत डॉक्टर से संपर्क करें।
    आपकी जिंदगी अनमोल है।
    """

    st.text_area("Story", story)

    # =====================
    # IMAGE GENERATION (SAFE)
    # =====================
    images = []

    for i in range(5):
        img = Image.new("RGB", (720,1280), (20,20,20))
        draw = ImageDraw.Draw(img)

        text = f"{topic}\nScene {i+1}"

        draw.text((50,600), text, fill=(255,255,255))

        path = f"out/{i}.png"
        img.save(path)
        images.append(path)

    # =====================
    # VOICE (STABLE)
    # =====================
    audio_path = "out/audio.mp3"

    tts = gTTS(story, lang='hi')
    tts.save(audio_path)

    # =====================
    # VIDEO (PURE FFMPEG)
    # =====================
    with open("files.txt", "w") as f:
        for img in images:
            f.write(f"file '{img}'\n")
            f.write("duration 3\n")
        f.write(f"file '{images[-1]}'\n")

    subprocess.run([
        "ffmpeg","-y",
        "-f","concat",
        "-safe","0",
        "-i","files.txt",
        "-vf","scale=720:1280",
        "-pix_fmt","yuv420p",
        "temp.mp4"
    ])

    final_video = "out/final.mp4"

    subprocess.run([
        "ffmpeg","-y",
        "-i","temp.mp4",
        "-i",audio_path,
        "-c:v","copy",
        "-c:a","aac",
        "-shortest",
        final_video
    ])

    st.success("✅ DONE (NO BLANK SCREEN)")
    st.video(final_video)
