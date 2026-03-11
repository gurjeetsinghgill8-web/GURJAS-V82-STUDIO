import streamlit as st
import os, asyncio, requests, edge_tts, subprocess, shutil, re
from groq import Groq
from urllib.parse import quote

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🏥", layout="centered")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🏥 GURJAS V82: PROFESSIONAL STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | Multi-Shot Medical Engine</p>", unsafe_allow_html=True)

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

if 'script_data' not in st.session_state: st.session_state.script_data = []

# 3. AGENTIC PROMPT: CLINICAL PERSONA + EMOTIONAL STORYTELLER
topic = st.text_input("💉 Enter Medical Topic:", placeholder="e.g., Understanding Heart Valve Blockage...")
mode = st.radio("Select Production Mode:", ["Short Reel (6 Shots)", "Full Documentary (12 Shots)"], horizontal=True)

if st.button("🚀 ACTIVATE PROFESSIONAL AGENTS"):
    with st.status("🔬 Agent Researcher & Storyteller Filtering Content...", expanded=True) as status:
        num_scenes = 6 if "Short" in mode else 12
        
        # ELI8 + Strict Clinical Constraint
        prompt = (
            f"Act as a Cardiac Surgeon and Master Teacher. Topic: {topic}. Break into {num_scenes} scenes. "
            "STRICT RULES: Use ONLY clinical keywords (e.g., 3D heart animation, surgery, hospital, anatomy). "
            "NO lifestyle, NO people in beds, NO suggestive/adult content. "
            "Script: Emotional Hinglish for a patient, simplified like an 8th grader. "
            "Format: SCENE_START | Medical_Keyword | Script | SCENE_END"
        )
        
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        scenes = re.findall(r"SCENE_START \| (.*?) \| (.*?) \| SCENE_END", res.choices[0].message.content)
        st.session_state.script_data = scenes
        status.update(label="✅ Clean Storyboard Ready!", state="complete")

# 4. MULTI-SHOT RENDERING (FFmpeg Direct)
if st.session_state.script_data:
    st.subheader("🎬 Storyboard Preview")
    full_script = " ".join([scr for kw, scr in st.session_state.script_data])
    
    if st.button("🎞️ RENDER MULTI-SHOT PROFESSIONAL VIDEO"):
        with st.spinner("⚡️ Stitching Clinical Visuals... (2-4 mins)"):
            try:
                # A. EMOTIONAL VOICE (SwaraNeural for better human feel)
                audio_path = f"{PROJECT_DIR}/voice.mp3"
                async def speak():
                    await edge_tts.Communicate(full_script, "hi-IN-SwaraNeural", rate="+10%").save(audio_path)
                asyncio.run(speak())

                # B. FETCH CLIPS (Forced Clinical Context)
                clip_files = []
                for idx, (kw, scr) in enumerate(st.session_state.script_data):
                    # FORCED FILTER: Suffix added to every search to prevent adult/irrelevant results
                    clinical_kw = f"{kw.strip()} medical cardiology hospital animation"
                    h = {"Authorization": PEXELS_KEY}
                    v_url = f"https://api.pexels.com/videos/search?query={quote(clinical_kw)}&per_page=1&orientation=portrait"
                    v_r = requests.get(v_url, headers=h).json()
                    
                    if 'videos' in v_r and v_r['videos']:
                        v_link = v_r['videos'][0]['video_files'][0]['link']
                        path = f"{PROJECT_DIR}/clips/c_{idx}.mp4"
                        with open(path, "wb") as f: f.write(requests.get(v_link).content)
                        
                        # Unify clips using FFmpeg TS format
                        uni = f"{PROJECT_DIR}/clips/u_{idx}.ts"
                        cmd = f'ffmpeg -y -i {path} -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24" -c:v libx264 -preset ultrafast -an {uni}'
                        subprocess.run(cmd, shell=True)
                        clip_files.append(uni)

                # C. ASSEMBLY
                concat_list = f"{PROJECT_DIR}/list.txt"
                with open(concat_list, "w") as f:
                    for c in clip_files: f.write(f"file '{os.path.abspath(c)}'\n")
                
                temp_v = f"{PROJECT_DIR}/temp.mp4"
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {temp_v}', shell=True)

                final_output = "GURJAS_CLINICAL_PRO.mp4"
                # Branding: Switched to White/Black for professionalism
                cmd_final = (
                    f'ffmpeg -y -i {temp_v} -i {audio_path} -c:v libx264 -c:a aac -map 0:v:0 -map 1:a:0 '
                    f'-vf "drawtext=text=\'DR. VASU MEMORIAL CLINIC\':fontcolor=white:fontsize=55:x=(w-text_w)/2:y=180:box=1:boxcolor=black@0.6" '
                    f'-shortest {final_output}'
                )
                subprocess.run(cmd_final, shell=True)

                st.video(final_output)
                st.download_button("📥 DOWNLOAD CLEAN VIDEO", open(final_output, "rb"), file_name=f"Gurjas_Pro_{topic}.mp4")
                st.success("🏥 Clinical Surgery Successful!")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
