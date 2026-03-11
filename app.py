import streamlit as st
import os, asyncio, requests, edge_tts, subprocess, shutil, re
from groq import Groq
from urllib.parse import quote

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: DIRECTOR'S STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | 2026 Multi-Shot Documentary Engine</p>", unsafe_allow_html=True)

# 2. KEYS & FOLDER SETUP
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
except:
    st.error("🚨 API Keys Missing! Please check Streamlit Secrets.")
    st.stop()

# Project Folder Management (Clean start for every project)
PROJECT_DIR = "current_project"
if os.path.exists(PROJECT_DIR): shutil.rmtree(PROJECT_DIR)
os.makedirs(f"{PROJECT_DIR}/clips")

# 3. AGENTIC PROMPT LOGIC
if 'script_data' not in st.session_state: st.session_state.script_data = []

topic = st.text_input("💉 Enter Medical Topic:", placeholder="e.g., Blockage in Heart Arteries...")
mode = st.radio("Select Production Mode:", ["Short Reel (5-6 Shots)", "Documentary (Parallel Storyline)"], horizontal=True)

if st.button("🚀 ACTIVATE PRODUCTION AGENTS"):
    with st.status("🔬 Agent Researcher & Storyteller working...", expanded=True) as status:
        num_scenes = 6 if "Short" in mode else 12
        
        # ELI8 (Explain Like I'm 8) + Expert Physician Persona
        prompt = (
            f"Act as a World-Class Cardiac Surgeon and a Master Teacher for 8th graders. "
            f"Topic: {topic}. Break this into {num_scenes} scenes. "
            f"Each scene must have a very specific visual keyword and 1 sentence of simplified medical explanation. "
            f"Format exactly as: SCENE_START | Keyword | Script | SCENE_END"
        )
        
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        raw_output = res.choices[0].message.content
        
        # Parse the scenes using the imported 're' module
        scenes = re.findall(r"SCENE_START \| (.*?) \| (.*?) \| SCENE_END", raw_output)
        st.session_state.script_data = scenes
        status.update(label="✅ Documentary Storyboard Ready!", state="complete")

# 4. MULTI-SHOT RENDERING ENGINE (FFmpeg Direct)
if st.session_state.script_data:
    st.subheader("🎬 Storyboard Preview")
    full_script = ""
    for idx, (kw, scr) in enumerate(st.session_state.script_data):
        st.write(f"**Shot {idx+1} ({kw}):** {scr}")
        full_script += f" {scr}"

    if st.button("🎞️ START MULTI-SHOT RENDERING"):
        with st.spinner("⚡️ Stitching Shots... (This may take 2-4 minutes)"):
            try:
                # A. AUDIO (Edge-TTS)
                audio_path = f"{PROJECT_DIR}/full_voice.mp3"
                async def speak():
                    await edge_tts.Communicate(full_script, "hi-IN-MadhurNeural", rate="+15%").save(audio_path)
                asyncio.run(speak())

                # B. FETCH MULTI-CLIPS (Pexels)
                clip_files = []
                for idx, (kw, scr) in enumerate(st.session_state.script_data):
                    h = {"Authorization": PEXELS_KEY}
                    v_url = f"https://api.pexels.com/videos/search?query={quote(kw.strip())}&per_page=1&orientation=portrait"
                    v_r = requests.get(v_url, headers=h).json()
                    if 'videos' in v_r and v_r['videos']:
                        v_link = v_r['videos'][0]['video_files'][0]['link']
                        path = f"{PROJECT_DIR}/clips/clip_{idx}.mp4"
                        with open(path, "wb") as f: f.write(requests.get(v_link).content)
                        clip_files.append(path)

                # C. INDUSTRIAL STITCHING (FFmpeg)
                # 1. Resize and unify all clips
                unified_clips = []
                for idx, clip in enumerate(clip_files):
                    unified_path = f"{PROJECT_DIR}/clips/uni_{idx}.ts"
                    cmd = f'ffmpeg -y -i {clip} -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24" -c:v libx264 -preset ultrafast -an {unified_path}'
                    subprocess.run(cmd, shell=True)
                    unified_clips.append(unified_path)

                # 2. Concat
                concat_list = f"{PROJECT_DIR}/concat_list.txt"
                with open(concat_list, "w") as f:
                    for c in unified_clips: f.write(f"file '{os.path.abspath(c)}'\n")
                
                temp_video = f"{PROJECT_DIR}/temp_full.mp4"
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {temp_video}', shell=True)

                # 3. Add Final Audio & Branding
                final_output = "GURJAS_PRODUCTION.mp4"
                cmd_final = (
                    f'ffmpeg -y -i {temp_video} -i {audio_path} -c:v libx264 -c:a aac -map 0:v:0 -map 1:a:0 '
                    f'-vf "drawtext=text=\'GURJAS MEDICAL ALERT\':fontcolor=yellow:fontsize=65:x=(w-text_w)/2:y=150:box=1:boxcolor=black@0.6" '
                    f'-shortest {final_output}'
                )
                subprocess.run(cmd_final, shell=True)

                st.video(final_output)
                st.download_button("📥 DOWNLOAD TO PHONE", open(final_output, "rb"), file_name=f"Gurjas_V82_{topic}.mp4")
                st.success("🏥 Multi-Shot Surgery Successful!")

            except Exception as e:
                st.error(f"⚠️ Complication: {e}")
