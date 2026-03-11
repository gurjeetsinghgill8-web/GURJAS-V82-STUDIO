import streamlit as st
import os, asyncio, requests, edge_tts, re
from groq import Groq
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from urllib.parse import quote

# UI Styling
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.title("🎬 GURJAS V82: AGENTIC STUDIO")

# Secrets
GROQ_KEY = st.secrets["GROQ_KEY"]
PEXELS_KEY = st.secrets["PEXELS_KEY"]
client = Groq(api_key=GROQ_KEY)

# Session State for persistence
if 'script' not in st.session_state: st.session_state.script = ""
if 'kw' not in st.session_state: st.session_state.kw = "heart health"

# --- AGENTIC FLOW ---
topic = st.text_input("Enter Topic:", placeholder="Silent Heart Attack...")

if st.button("🚀 PHASE 1 & 2: RESEARCH & SCRIPT"):
    with st.status("🔬 Agents are working...", expanded=True) as status:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Research {topic} and write a 35s viral Hinglish script. Output format: KEYWORD | SCRIPT"}],
            model="llama-3.3-70b-versatile"
        )
        data = res.choices[0].message.content
        st.session_state.kw, st.session_state.script = data.split("|", 1) if "|" in data else (topic, data)
        status.update(label="✅ Script Ready!", state="complete")

if st.session_state.script:
    st.subheader("Final Script:")
    final_scr = st.text_area("Review/Edit Script:", st.session_state.script, height=150)
    
    if st.button("🎬 PHASE 3: RENDER VIDEO"):
        with st.spinner("⚡️ Rendering HD Video (Wait 1-2 mins)..."):
            try:
                # 1. Voice Synthesis (Edge-TTS)
                v_file = "v.mp3"
                async def make_voice():
                    communicate = edge_tts.Communicate(final_scr, "hi-IN-MadhurNeural", rate="+20%")
                    await communicate.save(v_file)
                asyncio.run(make_voice())

                # 2. Fetch Video (Pexels)
                h = {"Authorization": PEXELS_KEY}
                v_url = f"https://api.pexels.com/videos/search?query={quote(st.session_state.kw.strip())}&per_page=1&orientation=portrait"
                v_r = requests.get(v_url, headers=h).json()
                video_link = v_r['videos'][0]['video_files'][0]['link']
                with open("r.mp4", "wb") as f: f.write(requests.get(video_link).content)

                # 3. Assemble (MoviePy)
                v_c = VideoFileClip("r.mp4"); a_c = AudioFileClip(v_file)
                v_c = v_c.set_duration(a_c.duration).resize(height=1920).crop(x_center=v_c.w/2, width=1080)
                
                # Overlay & Branding
                ov = ColorClip(size=(1080, 400), color=(0,0,0)).set_opacity(0.6).set_duration(a_c.duration).set_position(('center', 'center'))
                tx = TextClip("GURJAS MEDICAL ALERT", fontsize=70, color='yellow', font='Arial-Bold', method='caption', size=(900, None)).set_position('center').set_duration(a_c.duration)
                
                final_vid = CompositeVideoClip([v_c, ov, tx]).set_audio(a_c)
                final_vid.write_videofile("f.mp4", fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                st.video("f.mp4")
                st.download_button("📥 DOWNLOAD TO PHONE", open("f.mp4", "rb"), file_name="Gurjas_Medical.mp4")
                st.success("Surgery Successful! Video is ready for YouTube/Reels.")
            except Exception as e:
                st.error(f"Surgical Complication: {e}")
