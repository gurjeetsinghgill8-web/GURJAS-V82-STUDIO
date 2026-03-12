"""
╔══════════════════════════════════════════════════════════════════╗
║          GURJAS V9 — DR. VASU CONTENT FACTORY                   ║
║  Architecture: World-Class Agentic Medical Video Engine         ║
║                                                                  ║
║  Stack (100% FREE):                                              ║
║  • Groq (llama-3.3-70b)  → Script + Image Prompts              ║
║  • Pollinations.ai        → AI Medical Illustrations (FREE)     ║
║  • edge-tts MadhurNeural → Deep Male Hindi Voice               ║
║  • FFmpeg Ken Burns       → Cinematic Animation on Images      ║
║  • FFmpeg drawtext        → Burned Subtitles                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os, asyncio, requests, subprocess, shutil, re, time
import edge_tts
from groq import Groq
from urllib.parse import quote

# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG & WORLD-CLASS UI
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GURJAS V9 | Dr. Vasu Studio",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Rajdhani:wght@400;600;700&display=swap');

.stApp {
    background: radial-gradient(ellipse at top, #0d1f2d 0%, #000810 60%);
    color: #e8e8e8;
    font-family: 'Rajdhani', sans-serif;
}
.studio-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid rgba(255,215,0,0.2);
    margin-bottom: 2rem;
}
.studio-header h1 {
    font-family: 'Cinzel', serif;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 0.12em;
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.studio-header p { color: #8899aa; font-size: 1.05rem; letter-spacing: 0.25em; text-transform: uppercase; margin-top: 0.4rem; }
.stage-card { background: linear-gradient(135deg, rgba(255,215,0,0.04) 0%, rgba(255,140,0,0.02) 100%); border: 1px solid rgba(255,215,0,0.15); border-radius: 12px; padding: 1.5rem 2rem; margin: 1.5rem 0; position: relative; }
.stage-label { position: absolute; top: -13px; left: 20px; background: #FFD700; color: #000; font-family: 'Cinzel', serif; font-weight: 700; font-size: 0.72rem; letter-spacing: 0.18em; padding: 3px 14px; border-radius: 20px; }
.stButton > button { width: 100%; background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 1.05rem; letter-spacing: 0.1em; border: none; border-radius: 8px; height: 3.2em; cursor: pointer; text-transform: uppercase; }
.stButton > button:hover { background: linear-gradient(135deg, #FFF200, #FFB700); box-shadow: 0 8px 25px rgba(255,215,0,0.35); }
.stTextInput > div > div > input { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,215,0,0.25) !important; border-radius: 8px !important; color: #fff !important; }
.metric-row { display: flex; gap: 1rem; margin: 1rem 0; }
.metric-box { flex: 1; background: rgba(255,215,0,0.06); border: 1px solid rgba(255,215,0,0.2); border-radius: 8px; padding: 1rem; text-align: center; }
.metric-box .val { font-family: 'Cinzel', serif; font-size: 2rem; color: #FFD700; font-weight: 700; }
.metric-box .lbl { font-size: 0.75rem; color: #667; text-transform: uppercase; letter-spacing: 0.15em; margin-top: 0.2rem; }
[data-testid="stSidebar"] { background: rgba(5,10,20,0.95); border-right: 1px solid rgba(255,215,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="studio-header">
  <h1>🏥 GURJAS V9</h1>
  <p>Dr. Vasu Memorial Clinic &nbsp;·&nbsp; AI Director's Studio &nbsp;·&nbsp; Industrial Grade</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# KEYS & SESSION STATE
# ══════════════════════════════════════════════════════════════════
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("🚨 GROQ_KEY missing in Streamlit Secrets!")
    st.stop()

PROJECT_DIR = "gurjas_v9_vault"

for k, v in [("full_package", ""), ("scenes", []), ("angles", ""), ("render_done", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def fresh_vault():
    if os.path.exists(PROJECT_DIR):
        shutil.rmtree(PROJECT_DIR)
    for sub in ["images", "audio", "clips"]:
        os.makedirs(f"{PROJECT_DIR}/{sub}")


async def tts_generate(text: str, path: str):
    """
    hi-IN-MadhurNeural = deepest available male Hindi voice in edge-tts.
    rate=-8%, pitch=-15Hz = slower, more authoritative, closer to baritone.
    """
    await edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="-8%", pitch="-15Hz").save(path)


def get_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True
    )
    try:
        return max(float(r.stdout.strip()), 2.5)
    except Exception:
        return 4.0


def fetch_ai_image(prompt: str, idx: int, style: str) -> str:
    """
    Pollinations.ai — completely FREE, no API key.
    Generates a fresh AI medical illustration from scene content.
    """
    styles = {
        "cartoon":    "medical cartoon illustration, flat vector art, vibrant bold colors, clean lines, educational",
        "dramatic":   "cinematic medical scene, dramatic chiaroscuro lighting, dark moody atmosphere, ultra detailed",
        "realistic":  "hyper-realistic medical 3D render, photorealistic anatomy, clinical white background",
        "watercolor": "soft medical watercolor painting, gentle brush strokes, pastel palette, elegant artistic",
    }
    prefix = styles.get(style, styles["cartoon"])
    full = f"{prefix}, {prompt}, portrait 9:16 aspect ratio, professional medical education visual, no text overlay, no watermark"
    url = f"https://image.pollinations.ai/prompt/{quote(full)}?width=1080&height=1920&seed={idx * 137 + 42}&nologo=true&enhance=true"
    try:
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and len(r.content) > 5000:
            path = f"{PROJECT_DIR}/images/scene_{idx}.jpg"
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    except Exception:
        pass
    # Fallback: colored gradient frame
    fallback = f"{PROJECT_DIR}/images/fallback_{idx}.jpg"
    subprocess.run(
        f'ffmpeg -y -f lavfi -i "color=c=0d1f2d:size=1080x1920:rate=1" '
        f'-frames:v 1 "{fallback}" -loglevel quiet',
        shell=True
    )
    return fallback


def image_to_video_ken_burns(image_path: str, duration: float, idx: int) -> str:
    """
    Cinematic Ken Burns: alternates zoom-in/out with gentle pan.
    Turns static AI illustrations into documentary-style motion.
    """
    out = f"{PROJECT_DIR}/clips/raw_{idx}.ts"
    frames = max(int(duration * 25), 50)
    if idx % 3 == 0:
        zoom = "min(zoom+0.0015,1.5)"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif idx % 3 == 1:
        zoom = "if(eq(on,1),1.4,max(zoom-0.0015,1.0))"
        x, y = "iw/2-(iw/zoom/2)+on*0.3", "ih/3-(ih/zoom/3)"
    else:
        zoom = "min(zoom+0.001,1.3)"
        x, y = "iw/3-(iw/zoom/3)", "ih/2-(ih/zoom/2)"

    cmd = (
        f'ffmpeg -y -loop 1 -i "{image_path}" '
        f'-vf "zoompan=z=\'{zoom}\':d={frames}:x=\'{x}\':y=\'{y}\':s=1080x1920:fps=25,'
        f'scale=1080:1920" '
        f'-t {duration:.3f} -c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning'
    )
    subprocess.run(cmd, shell=True)
    return out if (os.path.exists(out) and os.path.getsize(out) > 500) else None


def burn_subtitle(clip: str, text: str, idx: int) -> str:
    """Burn clean white subtitle with dark backdrop at bottom."""
    out = f"{PROJECT_DIR}/clips/sub_{idx}.ts"
    safe = text.replace("'", "").replace('"', '').replace(":", " ").replace("%", "pct")[:70]
    cmd = (
        f'ffmpeg -y -i "{clip}" '
        f'-vf "drawtext=text=\'{safe}\':fontcolor=white:fontsize=40:'
        f'x=(w-text_w)/2:y=h-170:box=1:boxcolor=black@0.7:boxborderw=16" '
        f'-c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning'
    )
    subprocess.run(cmd, shell=True)
    return out if (os.path.exists(out) and os.path.getsize(out) > 500) else clip


def concat_ts(paths: list, out: str):
    lst = f"{PROJECT_DIR}/concat.txt"
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{out}" -loglevel warning', shell=True)


def concat_audio(paths: list, out: str):
    lst = f"{PROJECT_DIR}/alist.txt"
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{out}" -loglevel warning', shell=True)


def final_render(video: str, audio: str, output: str):
    """Mix audio+video, add clinic brand bar, cinematic color grade, vignette."""
    cmd = (
        f'ffmpeg -y -i "{video}" -i "{audio}" '
        f'-filter_complex "'
        f'[0:v]vignette=PI/6[v1];'
        f'[v1]eq=contrast=1.1:brightness=0.02:saturation=1.18[v2];'
        f'[v2]drawbox=y=0:x=0:w=iw:h=108:color=black@0.85:t=fill[v3];'
        f'[v3]drawtext=text=\'DR. VASU MEMORIAL CLINIC\':'
        f'fontcolor=#FFD700:fontsize=40:x=(w-text_w)/2:y=30[final]" '
        f'-map "[final]" -map 1:a '
        f'-c:v libx264 -preset fast -c:a aac -b:a 192k -shortest -movflags +faststart '
        f'"{output}" -loglevel warning'
    )
    subprocess.run(cmd, shell=True)


# ══════════════════════════════════════════════════════════════════
# SIDEBAR — IDEATION AGENT
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔬 IDEATION AGENT")
    broad_topic = st.text_input("Broad Topic:", placeholder="e.g. Silent Heart Attack")
    art_style = st.selectbox("🎨 Visual Style:", ["cartoon", "dramatic", "realistic", "watercolor"])
    num_scenes = st.slider("📽️ Scenes:", 4, 12, 6)

    if st.button("🔍 FIND 5 VIRAL ANGLES"):
        if broad_topic.strip():
            with st.spinner("Analyzing trends..."):
                r = client.chat.completions.create(
                    messages=[{"role": "user", "content":
                        f"Viral Hindi medical content strategist. Topic: {broad_topic}. "
                        f"Give 5 shocking, emotional video angle ideas in pure Hindi (Devanagari). "
                        f"1 punchy line each. Numbered 1-5. Be dramatic, fear/hope-inducing."}],
                    model="llama-3.3-70b-versatile", max_tokens=500
                )
                st.session_state.angles = r.choices[0].message.content

    if st.session_state.angles:
        st.info(st.session_state.angles)

    st.markdown("---")
    st.markdown("### 🛠️ Production Logs")
    log_box = st.empty()


# ══════════════════════════════════════════════════════════════════
# STAGE 1 — VIRAL CONTENT BRAIN
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="stage-card"><span class="stage-label">STAGE 1 — CONTENT BRAIN</span>', unsafe_allow_html=True)

main_topic = st.text_input(
    "💉 Medical Topic for Video:",
    placeholder="e.g. 3 Silent Signs of Heart Attack jo doctors bhi miss kar dete hain"
)

if st.button("⚡ GENERATE COMPLETE VIRAL PACKAGE"):
    if not main_topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.status("🧠 AI Director is crafting your viral package...", expanded=True) as s:
            st.write("Building script, image prompts, captions, hashtags...")

            master_prompt = f"""You are the world's best viral Hindi medical content director AND AI visual prompt engineer.

TOPIC: {main_topic}

Create a COMPLETE content package:

[HOOK]
One dramatic shocking opening line in Hindi. Creates fear or deep curiosity.

[CAPTION]
3-4 emotional Hindi lines for Instagram/YouTube. Ends with call to action.

[HASHTAGS]
20 hashtags mixing Hindi medical and English medical terms.

[THUMBNAIL_TEXT]
3-5 BOLD Hindi words. Curiosity-gap style. Works as thumbnail text.

[STORY]
A 3-line emotional patient story in Hindi. Feels real and relatable.

[CTA]
Dr. Vasu Memorial Clinic — Expert care mein aayein.

[SCENES]
Write exactly {num_scenes} scenes. Use this EXACT format per line:
SCENE | <3-4 word English medical keyword> | <1-2 sentence Hindi voice script> | <Detailed English AI image generation prompt: describe medical scene, mood, lighting, colors, style, composition — be very specific>

All {num_scenes} SCENE lines:"""

            res = client.chat.completions.create(
                messages=[{"role": "user", "content": master_prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=4000
            )
            raw = res.choices[0].message.content
            st.session_state.full_package = raw

            scenes_raw = re.findall(
                r"SCENE\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)(?=\nSCENE|\Z)",
                raw, re.DOTALL
            )
            st.session_state.scenes = [
                {
                    "keyword": m[0].strip(),
                    "hindi": m[1].strip().replace("\n", " "),
                    "image_prompt": m[2].strip().replace("\n", " ")
                }
                for m in scenes_raw if m[0].strip() and m[1].strip()
            ]
            n = len(st.session_state.scenes)
            s.update(label=f"✅ {n} scenes generated!", state="complete")

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.full_package:
    with st.expander("📋 FULL VIRAL PACKAGE — Click to Review & Copy"):
        st.markdown(st.session_state.full_package)

    sc = st.session_state.scenes
    if sc:
        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-box"><div class="val">{len(sc)}</div><div class="lbl">Scenes</div></div>
          <div class="metric-box"><div class="val">♂</div><div class="lbl">Madhur Voice</div></div>
          <div class="metric-box"><div class="val">{art_style}</div><div class="lbl">Visual Style</div></div>
          <div class="metric-box"><div class="val">₹0</div><div class="lbl">Total Cost</div></div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🎬 STORYBOARD PREVIEW"):
            for i, s in enumerate(sc):
                c1, c2 = st.columns([1, 2])
                c1.markdown(f"**Scene {i+1}**\n\n`{s['keyword']}`")
                c2.write(s['hindi'])
                c2.caption(f"🎨 {s['image_prompt'][:90]}...")
                st.divider()


# ══════════════════════════════════════════════════════════════════
# STAGE 2 — PRODUCTION ENGINE
# ══════════════════════════════════════════════════════════════════
if st.session_state.scenes:
    st.markdown('<div class="stage-card"><span class="stage-label">STAGE 2 — PRODUCTION ENGINE</span>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    add_subs = c1.checkbox("📝 Burn Subtitles", value=True)
    show_prev = c2.checkbox("👁️ Show Image Previews", value=True)

    if st.button("🎬 LAUNCH FULL AI PRODUCTION — INDUSTRIAL MODE"):
        fresh_vault()
        scenes = st.session_state.scenes
        prog = st.progress(0, text="Initializing...")
        clip_paths, audio_paths = [], []

        try:
            for idx, sc in enumerate(scenes):
                prog.progress(int(idx / len(scenes) * 75), text=f"⚙️ Scene {idx+1}/{len(scenes)}...")

                # 1. AI Image generation (Pollinations - FREE)
                log_box.write(f"🎨 AI Image: Scene {idx+1}...")
                img = fetch_ai_image(sc["image_prompt"], idx, art_style)

                # 2. Deep male voice TTS
                log_box.write(f"🎙️ Voice: Scene {idx+1}...")
                aud = f"{PROJECT_DIR}/audio/s{idx}.mp3"
                asyncio.run(tts_generate(sc["hindi"], aud))
                dur = get_duration(aud)

                # 3. Ken Burns animation
                log_box.write(f"🎥 Ken Burns: Scene {idx+1} ({dur:.1f}s)...")
                clip = image_to_video_ken_burns(img, dur, idx)
                if clip is None:
                    log_box.write(f"⚠️ Scene {idx+1} render failed, skipping.")
                    continue

                # 4. Subtitles
                if add_subs:
                    clip = burn_subtitle(clip, sc["hindi"], idx)

                clip_paths.append(clip)
                audio_paths.append(aud)
                log_box.write(f"✅ Scene {idx+1} done.")

                if show_prev and os.path.exists(img):
                    with st.expander(f"🖼️ Scene {idx+1} — {sc['keyword']}", expanded=False):
                        st.image(img, caption=sc["hindi"][:60])

            if not clip_paths:
                st.error("❌ No clips rendered. Check internet connection.")
                st.stop()

            prog.progress(80, text="🔗 Stitching scenes...")
            raw_vid = f"{PROJECT_DIR}/video_raw.mp4"
            concat_ts(clip_paths, raw_vid)

            prog.progress(87, text="🔊 Merging voice tracks...")
            fin_aud = f"{PROJECT_DIR}/final_audio.mp3"
            concat_audio(audio_paths, fin_aud)

            prog.progress(93, text="🎨 Applying grade + branding...")
            output_file = f"DrVasu_V9_{int(time.time())}.mp4"
            final_render(raw_vid, fin_aud, output_file)

            prog.progress(100, text="✅ Done!")

            if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
                st.session_state.render_done = True
                st.balloons()
                st.success("🏥 World-Class Medical Video Ready!")
                st.video(output_file)
                with open(output_file, "rb") as f:
                    st.download_button("📥 DOWNLOAD YOUR VIDEO", f, file_name=output_file, mime="video/mp4")

                size_mb = os.path.getsize(output_file) / (1024*1024)
                total_dur = sum(get_duration(a) for a in audio_paths)
                st.markdown(f"""
                <div class="metric-row">
                  <div class="metric-box"><div class="val">{len(clip_paths)}</div><div class="lbl">Scenes Rendered</div></div>
                  <div class="metric-box"><div class="val">{total_dur:.0f}s</div><div class="lbl">Duration</div></div>
                  <div class="metric-box"><div class="val">{size_mb:.1f}MB</div><div class="lbl">File Size</div></div>
                  <div class="metric-box"><div class="val">FREE</div><div class="lbl">Total Cost</div></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⚠️ Final file missing. Check logs above.")

        except Exception as e:
            import traceback
            st.error(f"⚠️ Error: {e}")
            st.code(traceback.format_exc())

    st.markdown("</div>", unsafe_allow_html=True)
