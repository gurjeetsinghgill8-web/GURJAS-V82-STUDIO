import streamlit as st
import os, asyncio, requests, edge_tts, re, subprocess
from groq import Groq
from urllib.parse import quote

# --- 2026 AGENTIC INFRASTRUCTURE ---
# We bypass the 'editor' sub-module entirely to avoid ModuleNotFoundError
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.video.VideoClip import TextClip, ColorClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.config import configure_settings
except ImportError:
    st.error("🚨 System Reconstruction Failed. Attempting Emergency Protocol...")
    st.stop()

# Force ImageMagick Binary Path
if os.path.exists("/usr/bin/convert"):
    configure_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: AGENTIC STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | 2026 Cloud Edition</p>", unsafe_allow_html=True)

# 2. KEYS & CLINIC VITALS
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
except:
    st.error("🚨 API Keys Missing! Please check Secrets.")
    st.stop()

if 'script' not in st.session_state: st.session_state.script = ""
if 'kw' not in st.session_state: st.session_state.kw = "cardiology"

# --- PHASE 1: THE RESEARCHER ---
topic = st.text_input("💉 Enter Medical Topic:", placeholder="e.g., Silent Heart Attack Symptoms...")

if st.button("🚀 ACTIVATE AGENTS"):
    with st.status("🔬 Agent Researcher scanning 2026 data...", expanded=True) as status:
        prompt = (f"Act as a Cardiac Surgeon. Research {topic}. "
                  "Write a 30s viral Hinglish script for Reels. "
                  "Format: KEYWORD | SCRIPT")
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        data = res.choices[0].message.content
        st.session_state.kw, st.session_state.script = data.split("|", 1) if "|" in data else (topic, data)
        status.update(label="✅ Medical Script Sterilized!", state="complete")

# --- PHASE 2: THE PRODUCTION ---
if st.session_state.script:
    final_scr = st.text_area("✍️ Review Script:", st.session_state.script, height=150)
    
    if st.button("🎬 RENDER 9:16 HD VIDEO"):
        with st.spinner("⚡️ Production in progress on Cloud... (60-90s)"):
            try:
                # A. AUDIO
                v_file = "voice.mp3"
                async def speak():
                    await edge_tts.Communicate(final_scr, "hi-IN-MadhurNeural", rate="+20%").save(v_file)
                asyncio.run(speak())

                # B. VISUALS
                h = {"Authorization": PEXELS_KEY}
                v_url = f"https://api.pexels.com/videos/search?query={quote(st.session_state.kw.strip())}&per_page=1&orientation=portrait"
                v_r = requests.get(v_url, headers=h).json()
                v_link = v_r['videos'][0]['video_files'][0]['link']
                with open("raw.mp4", "wb") as f: f.write(requests.get(v_link).content)

                # C. MODERN ASSEMBLY (MoviePy 2.0 Direct Striking)
                v_clip = VideoFileClip("raw.mp4")
                a_clip = AudioFileClip(v_file)
                
                # Resizing & Formatting
                duration = a_clip.duration
                v_clip = v_clip.with_duration(duration).resized(height=1920).cropped(x_center=v_clip.w/2, width=1080)
                
                # Branding
                overlay = ColorClip(size=(1080, 400), color=(0,0,0)).with_opacity(0.6).with_duration(duration).with_position('center')
                txt = TextClip(text="GURJAS MEDICAL ALERT", font_size=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).with_duration(duration).with_position('center')
                
                final_reel = CompositeVideoClip([v_clip, overlay, txt]).with_audio(a_clip)
                final_reel.write_videofile("out.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.video("out.mp4")
                st.download_button("📥 DOWNLOAD TO PHONE", open("out.mp4", "rb"), file_name="Gurjas_V82_Hit.mp4")
                st.success("✅ Surgery Successful! Download your video.")
                
            except Exception as e:
                st.error(f"⚠️ Complication: {e}")
