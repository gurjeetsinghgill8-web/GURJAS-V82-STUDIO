import streamlit as st
import os, asyncio, requests, edge_tts, re, time
import PIL.Image

# --- THE SURGICAL PATCH (Fixes the PIL.Image.ANTIALIAS error) ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# -------------------------------------------------------------

from groq import Groq
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from urllib.parse import quote

# 1. PAGE CONFIG & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: MOBILE STUDIO</h1>", unsafe_content_name=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic, Modinagar</p>", unsafe_content_name=True)

# 2. SECRETS LOADING (From Streamlit Advanced Settings)
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("🚨 API Keys Missing! Please add them in Streamlit Settings > Secrets.")
    st.stop()

# 3. SESSION STATE (Memory Management)
if 'script' not in st.session_state: st.session_state.script = ""
if 'kw' not in st.session_state: st.session_state.kw = "cardiology health"

# --- PHASE 1 & 2: AGENTIC RESEARCH & SCRIPTING ---
topic = st.text_input("💉 Enter Medical Topic:", placeholder="e.g., Silent Heart Attack Symptoms...")

if st.button("🚀 PHASE 1 & 2: GENERATE SCRIPT"):
    with st.status("🔬 Agent Researcher is analyzing medical data...", expanded=True) as status:
        # Prompting for high-tension medical script
        prompt = (f"Act as a Viral Medical Director and Cardiac Physician. Research {topic}. "
                  "Write a 35-second viral Hinglish script for YouTube Shorts. "
                  "Start with a SHOCKING medical fact. End with 'Visit Dr. Vasu Memorial Clinic'. "
                  "Format exactly as: KEYWORD | SCRIPT")
        
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        data = res.choices[0].message.content
        
        # Split Keyword and Script
        if "|" in data:
            st.session_state.kw, st.session_state.script = data.split("|", 1)
        else:
            st.session_state.kw, st.session_state.script = topic, data
            
        status.update(label="✅ Analysis & Script Ready!", state="complete")

# --- PHASE 3: VIDEO RENDERING ENGINE ---
if st.session_state.script:
    final_scr = st.text_area("✍️ Review/Edit Your Script:", st.session_state.script, height=150)
    
    if st.button("🎬 PHASE 3: RENDER VIDEO (9:16 HD)"):
        with st.spinner("⚡️ Creating Video... (This takes 60-90 seconds)"):
            try:
                # A. VOICE OVER (Edge-TTS)
                v_file = "v.mp3"
                async def make_voice():
                    communicate = edge_tts.Communicate(final_scr, "hi-IN-MadhurNeural", rate="+20%")
                    await communicate.save(v_file)
                asyncio.run(make_voice())

                # B. FETCH MEDICAL FOOTAGE (Pexels)
                h = {"Authorization": PEXELS_KEY}
                v_url = f"https://api.pexels.com/videos/search?query={quote(st.session_state.kw.strip())}&per_page=1&orientation=portrait"
                v_r = requests.get(v_url, headers=h).json()
                
                if 'videos' in v_r and len(v_r['videos']) > 0:
                    video_link = v_r['videos'][0]['video_files'][0]['link']
                else:
                    # Fallback if specific keyword fails
                    video_link = "https://www.pexels.com/download/video/3191572/" # Heart beating fallback
                
                with open("r.mp4", "wb") as f: f.write(requests.get(video_link).content)

                # C. ASSEMBLE (MoviePy)
                v_clip = VideoFileClip("r.mp4")
                a_clip = AudioFileClip(v_file)
                
                # Trim & Resize for Reels/Shorts (9:16)
                v_clip = v_clip.set_duration(a_clip.duration).resize(height=1920)
                v_clip = v_clip.crop(x_center=v_clip.w/2, width=1080)
                
                # Branding Overlay (Semi-transparent black box)
                overlay = ColorClip(size=(1080, 450), color=(0,0,0)).set_opacity(0.6).set_duration(a_clip.duration).set_position(('center', 'center'))
                
                # Main Text Branding
                text_brand = TextClip("GURJAS MEDICAL ALERT", fontsize=75, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).set_position('center').set_duration(a_clip.duration)
                
                # Final Composition
                final_video = CompositeVideoClip([v_clip, overlay, text_brand]).set_audio(a_clip)
                final_video.write_videofile("final_output.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                # Display & Download
                st.video("final_output.mp4")
                with open("final_output.mp4", "rb") as file:
                    st.download_button("📥 DOWNLOAD TO PHONE", file, file_name="Gurjas_Medical_Short.mp4", mime="video/mp4")
                
                st.success("✅ Surgery Successful! Download your video above.")
                
            except Exception as e:
                st.error(f"⚠️ Surgical Complication: {e}")
                st.info("Check if ImageMagick is installed in packages.txt")

# Cleanup temporary files (Optional)
if os.path.exists("v.mp3"): os.remove("v.mp3")
