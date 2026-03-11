import streamlit as st
import os, asyncio, requests, edge_tts, subprocess, shutil, re, time
from groq import Groq
from urllib.parse import quote
from mutagen.mp3 import MP3  # For exact per-scene timing

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V83: PRECISION STUDIO", page_icon="🎬", layout="wide")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V83: PRECISION DIRECTOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | No-MoviePy | Per-Scene Sync</p>", unsafe_allow_html=True)

# 2. CORE ENGINES
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
except:
    st.error("🚨 API Keys Missing! Check Streamlit Secrets.")
    st.stop()

# Persistent Vault Management (V83 Fix: Unique IDs)
if 'session_id' not in st.session_state: st.session_state.session_id = int(time.time())
PROJECT_DIR = f"vault_{st.session_state.session_id}"
os.makedirs(f"{PROJECT_DIR}/clips", exist_ok=True)

# 3. VOICE PERSONA SELECTION (Baritone Logic)
st.sidebar.header("🎙️ VOICE AUTHORITY")
voice_persona = st.sidebar.selectbox(
    "Select Style:", 
    ["Raza Murad (Deep Bass)", "Bachchan (Dignified)", "Standard Male"]
)
pitch_map = {"Raza Murad (Deep Bass)": "-25Hz", "Bachchan (Dignified)": "-12Hz", "Standard Male": "+0Hz"}

# 4. CONTENT SYNTHESIS (HINDI + STORYBOARD)
if 'script_data' not in st.session_state: st.session_state.script_data = []

topic = st.text_input("💉 Enter Medical Topic:", placeholder="e.g., Silent Heart Attack Symptoms...")
mode = st.radio("Mode:", ["Short Reel (6 Shots)", "Documentary (12 Shots)"], horizontal=True)

if st.button("🚀 ACTIVATE AGENTIC STORYBOARD"):
    with st.status("🧠 Agent Strategist Building V83 Package...", expanded=True):
        num = 6 if "Short" in mode else 12
        prompt = (
            f"Act as a Cardiac Surgeon. Topic: {topic}. Break into {num} scenes. "
            "STRICT RULE: PURE HINDI (Devanagari). "
            "Format: SCENE_START | Medical_Keyword | Hindi_Sentence | SCENE_END"
        )
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        st.session_state.script_data = re.findall(r"SCENE_START \| (.*?) \| (.*?) \| SCENE_END", res.choices[0].message.content)
        st.success("✅ V83 Storyboard Synchronized!")

# 5. THE PRECISION RENDERING ENGINE (V83 Upgrade)
if st.session_state.script_data:
    if st.button("🎬 RENDER PRECISION VIDEO"):
        progress_bar = st.progress(0)
        log = st.empty()
        stitched_files = []
        
        try:
            for idx, (kw, scr) in enumerate(st.session_state.script_data):
                # A. PER-SCENE VOICE (Exact Sync)
                s_audio = f"{PROJECT_DIR}/a_{idx}.mp3"
                async def gen():
                    await edge_tts.Communicate(scr, "hi-IN-MadhurNeural", pitch=pitch_map[voice_persona]).save(s_audio)
                asyncio.run(gen())
                
                # V83 Upgrade: Measure exact audio duration
                duration = MP3(s_audio).info.length
                
                # B. FETCH VIDEO WITH FALLBACK
                safe_kw = f"{kw.strip()} medical hospital anatomy"
                v_r = requests.get(f"https://api.pexels.com/videos/search?query={quote(safe_kw)}&per_page=1&orientation=portrait", 
                                   headers={"Authorization": PEXELS_KEY}).json()
                
                v_link = ""
                if 'videos' in v_r and v_r['videos']:
                    v_link = v_r['videos'][0]['video_files'][0]['link']
                else:
                    # Visual Fallback Logic
                    fallback = requests.get(f"https://api.pexels.com/videos/search?query=medical+hospital&per_page=1", 
                                            headers={"Authorization": PEXELS_KEY}).json()
                    v_link = fallback['videos'][0]['video_files'][0]['link']
                
                raw_v = f"{PROJECT_DIR}/r_{idx}.mp4"
                with open(raw_v, "wb") as f: f.write(requests.get(v_link).content)

                # C. FFmpeg PRECISION STITCH (Syncing Scene to Audio)
                s_final = f"{PROJECT_DIR}/s_{idx}.ts"
                # V83 Fix: Per-scene duration forcing + Auto-Captioning
                cmd = (
                    f'ffmpeg -y -i {raw_v} -i {s_audio} '
                    f'-vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24,'
                    f'drawtext=text=\'{scr[:40]}...\':fontcolor=yellow:fontsize=50:x=(w-text_w)/2:y=h-400:box=1:boxcolor=black@0.6" '
                    f'-t {duration} -c:v libx264 -preset ultrafast -c:a aac -shortest {s_final}'
                )
                subprocess.run(cmd, shell=True)
                stitched_files.append(s_final)
                progress_bar.progress((idx + 1) / len(st.session_state.script_data))
                log.write(f"✅ Scene {idx+1} Sync Successful.")

            # D. FINAL CONCATENATION (Industrial Concat)
            concat_list = f"{PROJECT_DIR}/list.txt"
            with open(concat_list, "w") as f:
                for s in stitched_files: f.write(f"file '{os.path.abspath(s)}'\n")
            
            final_out = "GURJAS_V83_FINAL.mp4"
            subprocess.run(f'ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {final_out}', shell=True)
            
            st.video(final_out)
            st.download_button("📥 DOWNLOAD V83 VIDEO", open(final_out, "rb"), file_name=final_out)
            st.success("🏥 Clinical Sync Complete! V83 Production Ready.")

        except Exception as e:
            st.error(f"⚠️ Complication: {e}")
