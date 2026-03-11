import streamlit as st
import os, asyncio, requests, edge_tts, subprocess, shutil, re
from groq import Groq
from urllib.parse import quote

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82: HINDI DIRECTOR", page_icon="🎬", layout="wide")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: HINDI DIRECTOR STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | Strictly Hindi Medical Authority</p>", unsafe_allow_html=True)

# 2. KEYS & FOLDERS
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
except:
    st.error("🚨 API Keys Missing! Please check Streamlit Secrets.")
    st.stop()

PROJECT_DIR = "current_project"
if os.path.exists(PROJECT_DIR): shutil.rmtree(PROJECT_DIR)
os.makedirs(f"{PROJECT_DIR}/clips")

# --- STAGE 0: SIDEBAR VIRAL RESEARCH ---
st.sidebar.header("🔬 RESEARCH AGENT")
broad_topic = st.sidebar.text_input("Enter Broad Topic (e.g., Heart Blockage):")
if st.sidebar.button("🔍 Find 5 Viral Hindi Angles"):
    with st.sidebar:
        with st.spinner("Analyzing..."):
            ideation_prompt = f"Give 5 shocking medical angles in PURE HINDI for {broad_topic} for a physician's social media."
            res = client.chat.completions.create(messages=[{"role": "user", "content": ideation_prompt}], model="llama-3.3-70b-versatile")
            st.info(res.choices[0].message.content)

# --- STAGE 1: PARALLEL MODES (Shorts vs Documentary) ---
tab1, tab2 = st.tabs(["📱 Short Reel Mode (6 Shots)", "🎥 Documentary Mode (12 Shots)"])

def generate_full_package(topic, num_scenes):
    # STRICT HINDI INSTRUCTION
    package_prompt = (
        f"Act as a World-Class Physician. Topic: {topic}. Break into {num_scenes} scenes. "
        "STRICT RULE: Everything (Script, Hooks, Captions) MUST be in PURE HINDI (Devanagari Script). "
        "NO ENGLISH words in the script except medical terms like 'Stent' or 'Bypass'. "
        "Format for Video Clips: SCENE_START | Medical_Keyword | Hindi_Script_Sentence | SCENE_END. "
        "Also provide: 1. Hook Line, 2. Emotional Caption, 3. 15 Hashtags, 4. Thumbnail Text."
    )
    res = client.chat.completions.create(messages=[{"role": "user", "content": package_prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

# Common UI for both tabs
def render_production_ui(content):
    st.subheader("📋 Viral Social Media Package (Hindi)")
    st.markdown(content)
    scenes = re.findall(r"SCENE_START \| (.*?) \| (.*?) \| SCENE_END", content)
    st.session_state.script_data = scenes

# --- TAB 1: SHORT REEL ---
with tab1:
    topic_short = st.text_input("💉 Topic for 60s Reel:", key="ts")
    if st.button("🚀 Generate Reel Package", key="br1"):
        content = generate_full_package(topic_short, 6)
        render_production_ui(content)

# --- TAB 2: DOCUMENTARY ---
with tab2:
    topic_doc = st.text_input("🎥 Topic for 3-5min Documentary:", key="td")
    if st.button("🚀 Generate Documentary Package", key="br2"):
        content = generate_full_package(topic_doc, 12)
        render_production_ui(content)

# --- STAGE 2: PRODUCTION ENGINE (MULTI-SHOT STITCHING) ---
if 'script_data' in st.session_state and st.session_state.script_data:
    st.divider()
    if st.button("🎬 RENDER FINAL VIDEO FROM STORYBOARD"):
        with st.spinner("⚡️ Stitching Multi-Shot Medical Scenes..."):
            try:
                # A. AUDIO (SwaraNeural for Deep Hindi Emotions)
                full_script = " ".join([scr for kw, scr in st.session_state.script_data])
                audio_path = f"{PROJECT_DIR}/voice.mp3"
                async def speak():
                    await edge_tts.Communicate(full_script, "hi-IN-SwaraNeural", rate="+10%").save(audio_path)
                asyncio.run(speak())

                # B. FETCH CLIPS
                clip_files = []
                for idx, (kw, scr) in enumerate(st.session_state.script_data):
                    safe_kw = f"{kw.strip()} medical hospital anatomy clinical"
                    v_url = f"https://api.pexels.com/videos/search?query={quote(safe_kw)}&per_page=1&orientation=portrait"
                    v_r = requests.get(v_url, headers={"Authorization": PEXELS_KEY}).json()
                    
                    if 'videos' in v_r and v_r['videos']:
                        v_link = v_r['videos'][0]['video_files'][0]['link']
                        path = f"{PROJECT_DIR}/clips/c_{idx}.mp4"
                        with open(path, "wb") as f: f.write(requests.get(v_link).content)
                        
                        # Unify clips to TS format for clean concatenation
                        uni = f"{PROJECT_DIR}/clips/u_{idx}.ts"
                        cmd = f'ffmpeg -y -i {path} -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24" -c:v libx264 -preset ultrafast -an {uni}'
                        subprocess.run(cmd, shell=True)
                        clip_files.append(uni)

                # C. ASSEMBLE (FFmpeg)
                concat_list = f"{PROJECT_DIR}/list.txt"
                with open(concat_list, "w") as f:
                    for c in clip_files: f.write(f"file '{os.path.abspath(c)}'\n")
                
                temp_v = f"{PROJECT_DIR}/temp.mp4"
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {temp_v}', shell=True)

                final_output = "GURJAS_HINDI_PRODUCTION.mp4"
                # Final stitch with Audio and Clinic Branding
                cmd_final = (
                    f'ffmpeg -y -i {temp_v} -i {audio_path} -c:v libx264 -c:a aac -map 0:v:0 -map 1:a:0 '
                    f'-vf "drawtext=text=\'DR. VASU MEMORIAL CLINIC\':fontcolor=white:fontsize=55:x=(w-text_w)/2:y=180:box=1:boxcolor=black@0.6" '
                    f'-shortest {final_output}'
                )
                subprocess.run(cmd_final, shell=True)

                st.video(final_output)
                st.download_button("📥 DOWNLOAD HINDI VIDEO", open(final_output, "rb"), file_name="Gurjas_Hindi_Video.mp4")
                st.success("✅ Multi-Shot Production Complete!")

            except Exception as e:
                st.error(f"⚠️ Production Error: {e}")
