import streamlit as st
import os, asyncio, requests, edge_tts, re, time
import PIL.Image

# --- THE SURGICAL PATCH (Fixes compatibility for all Pillow versions) ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    # In newer Pillow, ANTIALIAS is renamed to Resampling.LANCZOS
    try:
        from PIL import ImageResampling
        PIL.Image.ANTIALIAS = ImageResampling.LANCZOS
    except ImportError:
        PIL.Image.ANTIALIAS = PIL.Image.BICUBIC # Fallback
# -----------------------------------------------------------------------

from groq import Groq
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from urllib.parse import quote

# 1. PAGE CONFIG & BRANDING (Corrected Syntax)
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: MOBILE STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic, Modinagar</p>", unsafe_allow_html=True)

# 2. SECRETS LOADING
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("🚨 API Keys Missing in Streamlit Secrets!")
    st.stop()

# 3. SESSION STATE
if 'script' not in st.session_state: st.session_state.script = ""
if 'kw' not in st.session_state: st.session_state.kw = "medical health"

# --- PHASE 1 & 2: AGENTIC RESEARCH & SCRIPTING ---
topic = st.text_input("💉 Enter Medical Topic:", placeholder="e.g., Silent Heart Attack Symptoms...")

if st.button("🚀 PHASE 1 & 2: GENERATE SCRIPT"):
    with st.status("🔬 Analyzing medical data...", expanded=True) as status:
        prompt = (f"Act as a Cardiac Physician. Research {topic}. "
                  "Write a 35s viral Hinglish script. "
                  "Format: KEYWORD | SCRIPT")
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        data = res.choices[0].message.content
        if "|" in data:
            st.session_state.kw, st.session_state.script = data.split("|", 1)
        else:
            st.session_state.kw, st.session_state.script = topic, data
        status.update(label="✅ Analysis Ready!", state="complete")

# --- PHASE 3: VIDEO RENDERING ENGINE ---
if st.session_state.script:
    final_scr = st.text_area("✍️ Review Script:", st.session_state.script, height=150)
    
    if st.button("🎬 PHASE 3: RENDER VIDEO"):
        with st.spinner("⚡️ Creating Video..."):
            try:
                # A. VOICE OVER
                v_file = "v.mp3"
                async def make_voice():
                    communicate = edge_tts.Communicate(final_scr, "hi-IN-MadhurNeural", rate="+20%")
                    await communicate.save(v_file)
                asyncio.run(make_voice())

                # B. FETCH VIDEO
                h = {"Authorization": PEXELS_KEY}
                v_url = f"https://api.pexels.com/videos/search?query={quote(st.session_state.kw.strip())}&per_page=1&orientation=portrait"
                v_r = requests.get(v_url, headers=h).json()
                v_link = v_r['videos'][0]['video_files'][0]['link']
                with open("r.mp4", "wb") as f: f.write(requests.get(v_link).content)

                # C. ASSEMBLE (MoviePy)
                v_c = VideoFileClip("r.mp4"); a_c = AudioFileClip(v_file)
                v_c = v_c.set_duration(a_c.duration).resize(height=1920).crop(x_center=v_c.w/2, width=1080)
                
                ov = ColorClip(size=(1080, 400), color=(0,0,0)).set_opacity(0.6).set_duration(a_c.duration).set_position('center')
                tx = TextClip("GURJAS MEDICAL ALERT", fontsize=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).set_position('center').set_duration(a_c.duration)
                
                final_video = CompositeVideoClip([v_c, ov, tx]).set_audio(a_c)
                final_video.write_videofile("f.mp4", fps=24, codec="libx264", logger=None)
                
                st.video("f.mp4")
                with open("f.mp4", "rb") as file:
                    st.download_button("📥 DOWNLOAD TO PHONE", file, file_name="Gurjas_Short.mp4")
                
            except Exception as e:
                st.error(f"⚠️ Render Error: {e}")
