import streamlit as st
import os, asyncio, requests, edge_tts, subprocess, shutil, re
from groq import Groq
from urllib.parse import quote

# 1. UI & BRANDING
st.set_page_config(page_title="GURJAS V82: CONTENT SCIENTIST", page_icon="🧪", layout="wide")
st.markdown("<h1 style='text-align: center; color: #FFD700;'>🎬 GURJAS V82: CONTENT SCIENTIST</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Dr. Vasu Memorial Clinic | Medical Viral Authority Engine</p>", unsafe_allow_html=True)

# 2. KEYS & FOLDERS
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
    PEXELS_KEY = st.secrets["PEXELS_KEY"]
except:
    st.error("🚨 API Keys Missing in Streamlit Secrets!")
    st.stop()

PROJECT_DIR = "current_project"
if os.path.exists(PROJECT_DIR): shutil.rmtree(PROJECT_DIR)
os.makedirs(f"{PROJECT_DIR}/clips")

# --- PHASE 0: VIRAL IDEATION AGENT ---
st.sidebar.header("🔬 STAGE 0: TOPIC RESEARCH")
broad_topic = st.sidebar.text_input("Enter Broad Topic (e.g., Cholesterol):")
if st.sidebar.button("🔍 FIND 5 VIRAL ANGLES"):
    with st.sidebar:
        with st.spinner("Analyzing trends..."):
            ideation_prompt = f"As a Medical Content Strategist, give 5 shocking/viral angles for {broad_topic} that would engage 8th graders and adults. Focus on heart health."
            res = client.chat.completions.create(messages=[{"role": "user", "content": ideation_prompt}], model="llama-3.3-70b-versatile")
            st.info(res.choices[0].message.content)

# --- PHASE 1: THE FULL CONTENT PACKAGE ---
st.header("📲 STAGE 1: VIRAL PACKAGE GENERATOR")
main_topic = st.text_input("💉 Enter Specific Topic for Video:", placeholder="e.g., The 3AM Heart Attack Sign...")

if st.button("🚀 GENERATE COMPLETE VIRAL PACKAGE"):
    with st.status("🧠 Agent Strategist is building your package...", expanded=True) as status:
        # The Master Prompt for all 7 points
        package_prompt = (
            f"Act as a World-Class Cardiac Physician and Viral Strategist. Topic: {main_topic}. "
            "Generate a complete social media package including: "
            "1. 4-5 Viral Scripts (30-60s each, ELI8 style). "
            "2. 3-Second Attention-Grabbing Hooks. "
            "3. Emotional Captions with description. "
            "4. 15 Viral & Medical Hashtags. "
            "5. Thumbnail/First Screen Text Ideas. "
            "6. The Emotional Angle/Story. "
            "7. CTA. "
            "Also, for ONE of these scripts, provide a 6-scene storyboard in this format: "
            "SCENE_START | Medical_Keyword | Script_Sentence | SCENE_END"
        )
        
        res = client.chat.completions.create(messages=[{"role": "user", "content": package_prompt}], model="llama-3.3-70b-versatile")
        full_content = res.choices[0].message.content
        
        # Display the package clearly for Dr. Gill to read
        st.subheader("📋 YOUR VIRAL PACKAGE (Read & Copy)")
        st.markdown(full_content)
        
        # Parse scenes for the video engine
        scenes = re.findall(r"SCENE_START \| (.*?) \| (.*?) \| SCENE_END", full_content)
        st.session_state.script_data = scenes
        status.update(label="✅ Full Package & Storyboard Ready!", state="complete")

# --- PHASE 2: INDUSTRIAL PRODUCTION ---
if 'script_data' in st.session_state and st.session_state.script_data:
    st.divider()
    st.header("🎞️ STAGE 2: PRODUCTION (MULTI-SHOT)")
    if st.button("🎬 RENDER HD VIDEO FROM PACKAGE"):
        with st.spinner("⚡️ Stitching 6 Professional Shots..."):
            try:
                # A. VOICE (Emotional SwaraNeural)
                full_script = " ".join([scr for kw, scr in st.session_state.script_data])
                audio_path = f"{PROJECT_DIR}/voice.mp3"
                async def speak():
                    await edge_tts.Communicate(full_script, "hi-IN-SwaraNeural", rate="+12%").save(audio_path)
                asyncio.run(speak())

                # B. FETCH CLIPS (Forced Clinical Filter)
                clip_files = []
                for idx, (kw, scr) in enumerate(st.session_state.script_data):
                    safe_kw = f"{kw.strip()} medical hospital cardiology surgery"
                    v_url = f"https://api.pexels.com/videos/search?query={quote(safe_kw)}&per_page=1&orientation=portrait"
                    v_r = requests.get(v_url, headers={"Authorization": PEXELS_KEY}).json()
                    
                    if 'videos' in v_r and v_r['videos']:
                        v_link = v_r['videos'][0]['video_files'][0]['link']
                        path = f"{PROJECT_DIR}/clips/c_{idx}.mp4"
                        with open(path, "wb") as f: f.write(requests.get(v_link).content)
                        
                        uni = f"{PROJECT_DIR}/clips/u_{idx}.ts"
                        cmd = f'ffmpeg -y -i {path} -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24" -c:v libx264 -preset ultrafast -an {uni}'
                        subprocess.run(cmd, shell=True)
                        clip_files.append(uni)

                # C. ASSEMBLE & BRAND
                concat_list = f"{PROJECT_DIR}/list.txt"
                with open(concat_list, "w") as f:
                    for c in clip_files: f.write(f"file '{os.path.abspath(c)}'\n")
                
                temp_v = f"{PROJECT_DIR}/temp.mp4"
                subprocess.run(f'ffmpeg -y -f concat -safe 0 -i {concat_list} -c copy {temp_v}', shell=True)

                final_output = "GURJAS_VIRAL_HIT.mp4"
                cmd_final = (
                    f'ffmpeg -y -i {temp_v} -i {audio_path} -c:v libx264 -c:a aac -map 0:v:0 -map 1:a:0 '
                    f'-vf "drawtext=text=\'DR. VASU MEMORIAL CLINIC\':fontcolor=white:fontsize=55:x=(w-text_w)/2:y=180:box=1:boxcolor=black@0.6" '
                    f'-shortest {final_output}'
                )
                subprocess.run(cmd_final, shell=True)

                st.video(final_output)
                st.download_button("📥 DOWNLOAD VIRAL VIDEO", open(final_output, "rb"), file_name=f"Gurjas_Viral_{main_topic}.mp4")
                st.success("🏥 Clinical Content Ready for Social Media!")

            except Exception as e:
                st.error(f"⚠️ Render Complication: {e}")
