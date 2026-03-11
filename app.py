import streamlit as st
import os, asyncio, requests, edge_tts, subprocess, shutil, re
from groq import Groq
from urllib.parse import quote

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🏥", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏥 GURJAS V82: MEDICAL PROFESSIONAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | STRICT MEDICAL MODE</p>", unsafe_allow_html=True)

# 2. KEYS LOADING
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
except:
    st.error("🚨 Keys Missing!")
    st.stop()

PROJECT_DIR = "current_project"
if os.path.exists(PROJECT_DIR): shutil.rmtree(PROJECT_DIR)
os.makedirs(f"{PROJECT_DIR}/clips")

if 'script_data' not in st.session_state: st.session_state.script_data = []

# --- PHASE 1: THE RESEARCHER (Strict Constraints) ---
topic = st.text_input("💉 Medical Topic:", placeholder="e.g., Blockage in Heart Arteries...")

if st.button("🚀 GENERATE PROFESSIONAL STORYBOARD"):
    with st.status("🔬 Agent Researcher: Filtering Professional Content...", expanded=True) as status:
        # STRICT PROMPT: No lifestyle, No adult, Only Medical
        prompt = (
            f"Act as a Cardiac Surgeon. Topic: {topic}. Break into 6 scenes. "
            "STRICT RULES: Use ONLY medical, hospital, surgical, or clinical keywords. "
            "NO lifestyle, NO people on beds, NO suggestive content. "
            "Script must be in EMOTIONAL Hinglish for a patient. "
            "Format: SCENE_START | Medical_Keyword | Script | SCENE_END"
        )
        
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        scenes = re.findall(r"SCENE_START \| (.*?) \| (.*?) \| SCENE_END", res.choices[0].message.content)
        st.session_state.script_data = scenes
        status.update(label="✅ Professional Storyboard Ready!", state="complete")

# --- PHASE 2: RENDERING (Medical Filter) ---
if st.session_state.script_data:
    if st.button("🎞️ RENDER PROFESSIONAL VIDEO"):
        with st.spinner("⚡️ Stitching Medical Visuals..."):
            try:
                # A. EMOTIONAL VOICE (SwaraNeural is better)
                full_script = " ".join([scr for kw, scr in st.session_state.script_data])
                audio_path = f"{PROJECT_DIR}/voice.mp3"
                async def speak():
                    # hi-IN-SwaraNeural has more emotional depth
                    await edge_tts.Communicate(full_script, "hi-IN-SwaraNeural", rate="+10%").save(audio_path)
                asyncio.run(speak())

                # B. FETCH CLIPS (Forced Medical Context)
                clip_files = []
                for idx, (kw, scr) in enumerate(st.session_state.script_data):
                    # We ADD "medical clinic hospital" to every keyword search
                    safe_kw = f"{kw.strip()} medical hospital surgery laboratory"
                    v_url = f"https://api.pexels.com/videos/search?query={quote(safe_kw)}&per_page=1&orientation=portrait"
                    v_r = requests.get(v_url, headers={"Authorization": PEXELS_KEY}).json()
                    
                    if 'videos' in v_r and v_r['videos']:
                        v_link = v_r['videos'][0]['video_files'][0]['link']
                        path = f"{PROJECT_DIR}/clips/c_{idx}.mp4"
                        with open(path, "wb") as f: f.write(requests.get(v_link).content)
                        
                        # Resize/Unify
                        uni = f"{PROJECT_DIR}/clips/u_{idx}.ts"
                        cmd = f'ffmpeg -y -i {path} -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24" -c:v libx264 -an {uni}'
                        subprocess.run(cmd, shell=True)
                        clip_files.append(uni)

                # C. STITCH & BRAND
                concat_list = f"{PROJECT_DIR}/list.txt"
                with open(concat_list, "w") as f:
                    for c in clip_files: f.write(f"file '{os.path.abspath(c)}'\n")
                
                temp_v = f"{PROJECT_DIR}/temp.mp4"
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {temp_v}', shell=True)

                final_output = "GURJAS_STRICT_MEDICAL.mp4"
                # Branding is kept professional and clean
                cmd_final = (
                    f'ffmpeg -y -i {temp_v} -i {audio_path} -c:v libx264 -c:a aac -map 0:v:0 -map 1:a:0 '
                    f'-vf "drawtext=text=\'DR. VASU MEMORIAL CLINIC\':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=150:box=1:boxcolor=black@0.5" '
                    f'-shortest {final_output}'
                )
                subprocess.run(cmd_final, shell=True)

                st.video(final_output)
                st.download_button("📥 DOWNLOAD CLEAN VIDEO", open(final_output, "rb"), file_name="Gurjas_Professional.mp4")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
