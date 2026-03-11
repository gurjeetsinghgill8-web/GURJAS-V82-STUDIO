import streamlit as st
import os, asyncio, requests, edge_tts, subprocess
from groq import Groq
from urllib.parse import quote

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: INDUSTRIAL STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | 2026 FFmpeg Edition</p>", unsafe_allow_html=True)

# 2. KEYS LOADING
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 API Keys Missing in Streamlit Secrets!")
    st.stop()

if 'script' not in st.session_state: st.session_state.script = ""
if 'kw' not in st.session_state: st.session_state.kw = "heart health"

# --- PHASE 1: THE RESEARCHER ---
topic = st.text_input("💉 Enter Medical Topic:", placeholder="e.g., Heart attack vs Cardiac Arrest...")

if st.button("🚀 ACTIVATE AGENTS"):
    with st.status("🔬 Agent Researcher is analyzing...", expanded=True) as status:
        prompt = (f"Act as a Cardiac Surgeon. Research {topic}. "
                  "Write a 30s viral Hinglish script for Reels. "
                  "Format: KEYWORD | SCRIPT")
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        data = res.choices[0].message.content
        st.session_state.kw, st.session_state.script = data.split("|", 1) if "|" in data else (topic, data)
        status.update(label="✅ Script Ready!", state="complete")

# --- PHASE 2: THE INDUSTRIAL ENGINE (FFmpeg) ---
if st.session_state.script:
    final_scr = st.text_area("✍️ Review Script:", st.session_state.script, height=150)
    
    if st.button("🎬 RENDER 9:16 HD VIDEO"):
        with st.spinner("⚡️ FFmpeg is stitching your video... (60s)"):
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

                # C. FFmpeg SURGERY (Direct Command Line)
                # Combine video and audio, and overlay a simple branding text
                output_file = "final_output.mp4"
                
                # FFmpeg Command: Combine + Text Overlay + Resize
                # We use 'drawtext' filter which is standard in FFmpeg
                cmd = (
                    f'ffmpeg -y -i raw.mp4 -i voice.mp3 -c:v libx264 -c:a aac '
                    f'-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,'
                    f'drawtext=text=\'GURJAS MEDICAL ALERT\':fontcolor=yellow:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:boxborderw=20" '
                    f'-map 0:v:0 -map 1:a:0 -shortest {output_file}'
                )
                
                subprocess.run(cmd, shell=True, check=True)
                
                st.video(output_file)
                st.download_button("📥 DOWNLOAD TO PHONE", open(output_file, "rb"), file_name="Gurjas_V82_Video.mp4")
                st.success("✅ Surgery Successful! Video is ready.")
                
            except Exception as e:
                st.error(f"⚠️ Industrial Error: {e}")
                st.info("FFmpeg failed to process. Ensure packages.txt has 'ffmpeg'.")
