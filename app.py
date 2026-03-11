import streamlit as st
import os, asyncio, requests, edge_tts, subprocess, shutil, re, time
from groq import Groq
from urllib.parse import quote

# 1. UI & BRANDING (EXECUTIVE DASHBOARD)
st.set_page_config(page_title="GURJAS V82: DIRECTOR STUDIO", page_icon="🏥", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FFD700; color: black; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #1e1e1e; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: AGENTIC DIRECTOR STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em;'>Dr. Vasu Memorial Clinic | The Gold Standard in Medical Automation</p>", unsafe_allow_html=True)

# 2. CORE SYSTEMS & KEYS
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
except Exception:
    st.error("🚨 Critical Error: API Keys are missing in Secrets!")
    st.stop()

# Project Environment Management
PROJECT_DIR = "gurjas_production_vault"
if os.path.exists(PROJECT_DIR): shutil.rmtree(PROJECT_DIR)
os.makedirs(f"{PROJECT_DIR}/clips")

if 'full_package' not in st.session_state: st.session_state.full_package = ""
if 'script_data' not in st.session_state: st.session_state.script_data = []

# --- STAGE 0: SIDEBAR IDEATION AGENT ---
with st.sidebar:
    st.header("🔬 RESEARCH & IDEATION")
    broad_topic = st.text_input("Enter Broad Medical Topic:", placeholder="e.g., Blocked Arteries")
    if st.button("🔍 FIND 5 VIRAL HINDI ANGLES"):
        with st.spinner("Agent Researcher is scanning trends..."):
            ideation_prompt = f"Act as a Medical Viral Strategist. Give 5 shocking/emotional medical angles in STRICT HINDI for {broad_topic}. Focus on patient relatability."
            res = client.chat.completions.create(messages=[{"role": "user", "content": ideation_prompt}], model="llama-3.3-70b-versatile")
            st.info(res.choices[0].message.content)
    st.divider()
    st.markdown("### 🛠️ Production Logs")
    log_area = st.empty()

# --- STAGE 1: THE 7-POINT VIRAL PACKAGE ENGINE ---
st.header("📲 STAGE 1: VIRAL CONTENT SYNTHESIS")
main_topic = st.text_input("💉 Enter Specific Topic for Production:", placeholder="e.g., 3 Silent Signs of Heart Attack...")
prod_mode = st.radio("Select Workflow Mode:", ["📱 Shorts (6 Shots)", "🎥 Documentary (12 Shots)"], horizontal=True)

if st.button("🚀 ACTIVATE AGENTIC PACKAGE GENERATOR"):
    with st.status("🧠 Agent Strategist is building the 7-Point Package...", expanded=True) as status:
        num_scenes = 6 if "Shorts" in prod_mode else 12
        
        # The Master Prompt (Strict Hindi, Expert Teacher, 7 Points)
        master_prompt = (
            f"Act as a World-Class Physician and Viral Content Director. Topic: {main_topic}. "
            f"Generate a complete social media package in STRICT HINDI (Devanagari). "
            "1. 4-5 Viral Scripts (30-60s, ELI8 style). "
            "2. 3-Second Shocking Hook Line. "
            "3. Emotional Caption & Description. "
            "4. 15 Viral & Medical Hashtags. "
            "5. Thumbnail Screen Text. "
            "6. Patient-Connect Emotional Story. "
            "7. CTA: 'Visit Dr. Vasu Memorial Clinic'. "
            f"ALSO, break the script into {num_scenes} scenes in this format: "
            "SCENE_START | Medical_Keyword | Hindi_Script_Sentence | SCENE_END"
        )
        
        res = client.chat.completions.create(messages=[{"role": "user", "content": master_prompt}], model="llama-3.3-70b-versatile")
        st.session_state.full_package = res.choices[0].message.content
        st.session_state.script_data = re.findall(r"SCENE_START \| (.*?) \| (.*?) \| SCENE_END", st.session_state.full_package)
        status.update(label="✅ Viral Package & Storyboard Ready!", state="complete")

# Display the Full Package for Review
if st.session_state.full_package:
    with st.expander("👁️ REVIEW FULL VIRAL PACKAGE", expanded=True):
        st.markdown(st.session_state.full_package)

# --- STAGE 2: THE INDUSTRIAL FFmpeg ENGINE ---
if st.session_state.script_data:
    st.divider()
    st.header("🎞️ STAGE 2: MULTI-SHOT INDUSTRIAL PRODUCTION")
    
    if st.button("🎬 START MECHANICAL RENDERING (FFmpeg Direct)"):
        with st.spinner("⚡️ FFmpeg is stitching your masterpiece..."):
            try:
                # A. HUMAN-LIKE VOICE SYNTHESIS (SwaraNeural for Deep Emotions)
                audio_path = f"{PROJECT_DIR}/final_voice.mp3"
                full_script = " ".join([scr for kw, scr in st.session_state.script_data])
                
                async def generate_voice():
                    # SwaraNeural is the most human-like emotional Hindi voice in edge-tts
                    await edge_tts.Communicate(full_script, "hi-IN-SwaraNeural", rate="+10%").save(audio_path)
                
                asyncio.run(generate_voice())
                log_area.write("✅ Voiceover Synthesis Complete.")

                # B. AGENTIC VISUAL ACQUISITION (Multi-Shot)
                clip_paths = []
                for idx, (kw, scr) in enumerate(st.session_state.script_data):
                    # Force Clinical Keywords to avoid adult/suggestive content
                    safe_kw = f"{kw.strip()} medical hospital cardiology anatomy clinical"
                    v_url = f"https://api.pexels.com/videos/search?query={quote(safe_kw)}&per_page=1&orientation=portrait"
                    v_r = requests.get(v_url, headers={"Authorization": PEXELS_KEY}).json()
                    
                    if 'videos' in v_r and v_r['videos']:
                        v_link = v_r['videos'][0]['video_files'][0]['link']
                        raw_path = f"{PROJECT_DIR}/clips/raw_{idx}.mp4"
                        with open(raw_path, "wb") as f: f.write(requests.get(v_link).content)
                        
                        # Unify clips for clean concatenation (1080x1920, 24fps)
                        unified_path = f"{PROJECT_DIR}/clips/uni_{idx}.ts"
                        cmd_uni = (
                            f'ffmpeg -y -i {raw_path} -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24" '
                            f'-c:v libx264 -preset ultrafast -an {unified_path}'
                        )
                        subprocess.run(cmd_uni, shell=True)
                        clip_paths.append(unified_path)
                        log_area.write(f"✅ Shot {idx+1} Processed.")

                # C. FINAL STITCHING (The Direct Surgical Strike)
                concat_list = f"{PROJECT_DIR}/concat_list.txt"
                with open(concat_list, "w") as f:
                    for c in clip_paths: f.write(f"file '{os.path.abspath(c)}'\n")
                
                temp_video = f"{PROJECT_DIR}/temp_merged.mp4"
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {temp_video}', shell=True)

                # D. BRANDING & OVERLAY
                final_output = f"GURJAS_V82_{int(time.time())}.mp4"
                cmd_final = (
                    f'ffmpeg -y -i {temp_video} -i {audio_path} -c:v libx264 -c:a aac -map 0:v:0 -map 1:a:0 '
                    f'-vf "drawtext=text=\'DR. VASU MEMORIAL CLINIC\':fontcolor=white:fontsize=55:x=(w-text_w)/2:y=180:box=1:boxcolor=black@0.6" '
                    f'-shortest {final_output}'
                )
                subprocess.run(cmd_final, shell=True)

                # E. DELIVERY
                st.video(final_output)
                st.download_button("📥 DOWNLOAD YOUR VIRAL HIT", open(final_output, "rb"), file_name=final_output)
                st.success("🏥 Multi-Shot Surgery Successful! Your medical content is live.")
                
            except Exception as e:
                st.error(f"⚠️ Surgical Complication: {e}")
