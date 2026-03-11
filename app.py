import streamlit as st
import os, asyncio, requests, edge_tts, re
from groq import Groq
from urllib.parse import quote
import PIL.Image

# --- 2026 SURGICAL PATCH: PILLOW 10+ COMPATIBILITY ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    from PIL import ImageResampling
    PIL.Image.ANTIALIAS = ImageResampling.LANCZOS

# --- MODERN MOVIEPY 2.0 IMPORTS ---
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.config import configure_settings

# --- PERMANENT IMAGEMAGICK PATH (STREAMLIT CLOUD LINUX) ---
if os.path.exists("/usr/bin/convert"):
    configure_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: CLOUD STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | 2026 Agentic Edition</p>", unsafe_allow_html=True)

# 2. SECRETS (From Streamlit Dashboard)
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 API Keys missing in Streamlit Secrets! Setup 'GROQ_KEY' and 'PEXELS_KEY'.")
    st.stop()

# 3. PERSISTENT MEMORY (CLAUDE.md Strategy)
if 'script' not in st.session_state: st.session_state.script = ""
if 'kw' not in st.session_state: st.session_state.kw = "cardiology"

# --- STAGE 1 & 2: AGENTIC BRAIN (RESEARCH & SCRIPT) ---
topic = st.text_input("💉 Enter Topic:", placeholder="e.g., Why Heart Failure happens at night?")

if st.button("🚀 ACTIVATE AGENTS (Research & Draft)"):
    with st.status("🔬 Agent Researcher scanning 2026 medical trends...", expanded=True) as status:
        prompt = (f"Act as a Cardiac Surgeon. Research {topic}. "
                  "Write a 35s viral Hinglish script. "
                  "Format: KEYWORD | SCRIPT")
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        data = res.choices[0].message.content
        st.session_state.kw, st.session_state.script = data.split("|", 1) if "|" in data else (topic, data)
        status.update(label="✅ Medical Script Sterilized & Ready!", state="complete")

# --- STAGE 3: CLOUD PRODUCTION (VIDEO RENDER) ---
if st.session_state.script:
    final_scr = st.text_area("✍️ Review Script:", st.session_state.script, height=150)
    
    if st.button("🎬 RENDER 9:16 HD VIDEO"):
        with st.spinner("⚡️ Production in progress on Streamlit Cloud..."):
            try:
                # A. AUDIO (Edge-TTS)
                v_file = "voice_output.mp3"
                async def generate_audio():
                    await edge_tts.Communicate(final_scr, "hi-IN-MadhurNeural", rate="+20%").save(v_file)
                asyncio.run(generate_audio())

                # B. VISUALS (Pexels)
                h = {"Authorization": PEXELS_KEY}
                v_url = f"https://api.pexels.com/videos/search?query={quote(st.session_state.kw.strip())}&per_page=1&orientation=portrait"
                v_r = requests.get(v_url, headers=h).json()
                video_link = v_r['videos'][0]['video_files'][0]['link']
                with open("raw_video.mp4", "wb") as f: f.write(requests.get(video_link).content)

                # C. SURGICAL ASSEMBLY (MoviePy 2.0 Syntax)
                v_clip = VideoFileClip("raw_video.mp4")
                a_clip = AudioFileClip(v_file)
                
                # Resize and Format for Reels
                v_clip = v_clip.with_duration(a_clip.duration).resized(height=1920)
                v_clip = v_clip.cropped(x_center=v_clip.w/2, width=1080)
                
                # Professional Branding
                overlay = ColorClip(size=(1080, 400), color=(0,0,0)).with_opacity(0.6).with_duration(a_clip.duration).with_position('center')
                txt = TextClip(text="GURJAS MEDICAL ALERT", font_size=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).with_duration(a_clip.duration).with_position('center')
                
                final_video = CompositeVideoClip([v_clip, overlay, txt]).with_audio(a_clip)
                final_video.write_videofile("final_reel.mp4", fps=24, codec="libx264", audio_codec="aac")
                
                st.video("final_reel.mp4")
                st.download_button("📥 DOWNLOAD TO PHONE", open("final_reel.mp4", "rb"), file_name="Gurjas_V82_Video.mp4")
                st.success("🏥 Surgery Successful! Video is ready for YouTube.")
                
            except Exception as e:
                st.error(f"⚠️ Render Error: {e}")
