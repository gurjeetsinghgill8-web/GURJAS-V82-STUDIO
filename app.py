import streamlit as st
import os, asyncio, requests, edge_tts, re
from groq import Groq
from urllib.parse import quote

# --- 2026 ROBUST PILLOW PATCH ---
import PIL.Image
if not hasattr(PIL.Image, 'Resampling'):
    # Fallback for very old environments
    LANCZOS_METHOD = PIL.Image.LANCZOS if hasattr(PIL.Image, 'LANCZOS') else 1
else:
    LANCZOS_METHOD = PIL.Image.Resampling.LANCZOS
# -------------------------------

from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.config import configure_settings

# Force ImageMagick Path for Streamlit Cloud Linux
if os.path.exists("/usr/bin/convert"):
    configure_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: MOBILE STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic, Modinagar</p>", unsafe_allow_html=True)

# 2. SECRETS LOADING
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 API Keys Missing! Please check Streamlit Secrets.")
    st.stop()

# 3. SESSION MEMORY
if 'script' not in st.session_state: st.session_state.script = ""
if 'kw' not in st.session_state: st.session_state.kw = "heart health"

# --- AGENTIC STAGE 1 & 2 ---
topic = st.text_input("💉 Enter Topic:", placeholder="e.g., Silent Heart Attack Symptoms...")

if st.button("🚀 ACTIVATE AGENTIC RESEARCH"):
    with st.status("🔬 Agent Researcher is analyzing data...", expanded=True) as status:
        prompt = (f"Act as a Cardiac Physician. Research {topic}. "
                  "Write a 30s viral Hinglish script for Reels. "
                  "Format: KEYWORD | SCRIPT")
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        data = res.choices[0].message.content
        st.session_state.kw, st.session_state.script = data.split("|", 1) if "|" in data else (topic, data)
        status.update(label="✅ Analysis Ready!", state="complete")

# --- AGENTIC STAGE 3: VIDEO ENGINE ---
if st.session_state.script:
    final_scr = st.text_area("✍️ Review Script:", st.session_state.script, height=150)
    
    if st.button("🎬 RENDER 9:16 HD VIDEO"):
        with st.spinner("⚡️ Operation in progress on Cloud... (60s)"):
            try:
                # A. AUDIO (Edge-TTS)
                v_file = "voice.mp3"
                async def speak():
                    await edge_tts.Communicate(final_scr, "hi-IN-MadhurNeural", rate="+20%").save(v_file)
                asyncio.run(speak())

                # B. VIDEO (Pexels)
                h = {"Authorization": PEXELS_KEY}
                v_url = f"https://api.pexels.com/videos/search?query={quote(st.session_state.kw.strip())}&per_page=1&orientation=portrait"
                v_r = requests.get(v_url, headers=h).json()
                v_link = v_r['videos'][0]['video_files'][0]['link']
                with open("raw.mp4", "wb") as f: f.write(requests.get(v_link).content)

                # C. MODERN ASSEMBLY (MoviePy 2.0+)
                v_clip = VideoFileClip("raw.mp4")
                a_clip = AudioFileClip(v_file)
                
                # Resizing for Reels
                v_clip = v_clip.with_duration(a_clip.duration).resized(height=1920)
                v_clip = v_clip.cropped(x_center=v_clip.w/2, width=1080)
                
                # Branding
                overlay = ColorClip(size=(1080, 400), color=(0,0,0)).with_opacity(0.6).with_duration(a_clip.duration).with_position('center')
                txt = TextClip(text="GURJAS MEDICAL ALERT", font_size=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).with_duration(a_clip.duration).with_position('center')
                
                final_reel = CompositeVideoClip([v_clip, overlay, txt]).with_audio(a_clip)
                final_reel.write_videofile("out.mp4", fps=24, codec="libx264", audio_codec="aac")
                
                st.video("out.mp4")
                st.download_button("📥 DOWNLOAD TO PHONE", open("out.mp4", "rb"), file_name="Gurjas_V82_Hit.mp4")
                st.success("✅ Surgery Successful! Download your video.")
                
            except Exception as e:
                st.error(f"⚠️ Complication: {e}")
