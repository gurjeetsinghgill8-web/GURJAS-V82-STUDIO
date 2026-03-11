import streamlit as st
import os, asyncio, requests, edge_tts, re
from groq import Groq
from urllib.parse import quote
import PIL.Image

# --- 2026 PILLOW COMPATIBILITY BYPASS ---
# This ensures no matter what version of Pillow is installed, it won't crash.
if not hasattr(PIL.Image, 'ANTIALIAS'):
    try:
        # Check for new Resampling attribute
        PIL.Image.ANTIALIAS = getattr(PIL.Image, 'LANCZOS', getattr(PIL.Image, 'BICUBIC', 1))
    except:
        pass
# -----------------------------------------

# Import MoviePy with modern 2.0 structure
try:
    from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
    from moviepy.config import configure_settings
except ImportError:
    # Fallback for older MoviePy environments
    from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
    from moviepy.config import change_settings as configure_settings

# --- CRITICAL: IMAGEMAGICK PATH FOR LINUX ---
if os.path.exists("/usr/bin/convert"):
    configure_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: CLOUD STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic, Modinagar</p>", unsafe_allow_html=True)

# 2. SECRETS LOADING
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 API Keys Missing! Please add them in Streamlit Secrets.")
    st.stop()

# 3. PERSISTENT STATE
if 'script' not in st.session_state: st.session_state.script = ""
if 'kw' not in st.session_state: st.session_state.kw = "heart health"

# --- AGENTIC STAGE 1: RESEARCH & SCRIPT ---
topic = st.text_input("💉 Enter Medical Topic:", placeholder="e.g., Silent Heart Attack Symptoms...")

if st.button("🚀 ACTIVATE AGENTIC RESEARCH"):
    with st.status("🔬 Agent Researcher is analyzing 2026 data...", expanded=True) as status:
        prompt = (f"Act as a Cardiac Physician. Research {topic}. "
                  "Write a 30s viral Hinglish script. Format: KEYWORD | SCRIPT")
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        data = res.choices[0].message.content
        st.session_state.kw, st.session_state.script = data.split("|", 1) if "|" in data else (topic, data)
        status.update(label="✅ Analysis & Script Ready!", state="complete")

# --- AGENTIC STAGE 2: CLOUD PRODUCTION ---
if st.session_state.script:
    final_scr = st.text_area("✍️ Review/Edit Script:", st.session_state.script, height=150)
    
    if st.button("🎬 RENDER 9:16 HD VIDEO"):
        with st.spinner("⚡️ Operation in progress on Cloud... (60-90s)"):
            try:
                # A. AUDIO (Edge-TTS)
                v_file = "voice.mp3"
                async def speak():
                    await edge_tts.Communicate(final_scr, "hi-IN-MadhurNeural", rate="+20%").save(v_file)
                asyncio.run(speak())

                # B. VISUALS (Pexels)
                h = {"Authorization": PEXELS_KEY}
                v_url = f"https://api.pexels.com/videos/search?query={quote(st.session_state.kw.strip())}&per_page=1&orientation=portrait"
                v_r = requests.get(v_url, headers=h).json()
                v_link = v_r['videos'][0]['video_files'][0]['link']
                with open("raw.mp4", "wb") as f: f.write(requests.get(v_link).content)

                # C. ASSEMBLY (MoviePy 2.0 Compatible Syntax)
                v_clip = VideoFileClip("raw.mp4")
                a_clip = AudioFileClip(v_file)
                
                # Check for MoviePy 2.0 vs 1.0 method names
                duration = a_clip.duration
                if hasattr(v_clip, 'with_duration'):
                    v_clip = v_clip.with_duration(duration).resized(height=1920).cropped(x_center=v_clip.w/2, width=1080)
                    overlay = ColorClip(size=(1080, 400), color=(0,0,0)).with_opacity(0.6).with_duration(duration).with_position('center')
                    txt = TextClip(text="GURJAS MEDICAL ALERT", font_size=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).with_duration(duration).with_position('center')
                    final_video = CompositeVideoClip([v_clip, overlay, txt]).with_audio(a_clip)
                else:
                    v_clip = v_clip.set_duration(duration).resize(height=1920).crop(x_center=v_c.w/2, width=1080)
                    overlay = ColorClip(size=(1080, 400), color=(0,0,0)).set_opacity(0.6).set_duration(duration).set_position('center')
                    txt = TextClip("GURJAS MEDICAL ALERT", fontsize=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).set_duration(duration).set_position('center')
                    final_video = CompositeVideoClip([v_clip, overlay, txt]).set_audio(a_clip)

                final_video.write_videofile("f.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.video("f.mp4")
                st.download_button("📥 DOWNLOAD TO PHONE", open("f.mp4", "rb"), file_name="Gurjas_Medical_V82.mp4")
                st.success("✅ Surgery Successful! Download your video.")
                
            except Exception as e:
                st.error(f"⚠️ Render Error: {e}")
