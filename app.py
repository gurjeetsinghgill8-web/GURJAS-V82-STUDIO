"""
╔══════════════════════════════════════════════════════════════════════╗
║   GURJAS V10 — DR. VASU CONTENT FACTORY                            ║
║   World-Class Agentic Medical Cartoon Video Engine                 ║
║                                                                      ║
║   GUARANTEED CARTOON STACK (100% FREE, 100% OFFLINE VISUALS):      ║
║   • Groq llama-3.3-70b  → Script + scene metadata                  ║
║   • PIL / Pillow         → Programmatic cartoon illustrations       ║
║     (Always works, always relevant, no API, no internet needed)     ║
║   • edge-tts Madhur      → Deep authoritative male Hindi voice      ║
║   • FFmpeg Ken Burns     → Cinematic zoom animation                 ║
║   • FFmpeg drawtext      → Burned Hindi subtitles                   ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os, asyncio, requests, subprocess, shutil, re, time, math, json
import edge_tts
from groq import Groq
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from urllib.parse import quote

# ══════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GURJAS V10 | Dr. Vasu Studio",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Rajdhani:wght@400;600;700&display=swap');

.stApp { background: radial-gradient(ellipse at top, #0a1628 0%, #000509 70%); color: #e8e8e8; font-family: 'Rajdhani', sans-serif; }
.hdr { text-align:center; padding:2.5rem 1rem 1.5rem; border-bottom:1px solid rgba(255,215,0,.18); margin-bottom:2rem; }
.hdr h1 { font-family:'Cinzel',serif; font-size:2.8rem; font-weight:900; letter-spacing:.14em;
           background:linear-gradient(135deg,#FFD700 0%,#FFA500 50%,#FFD700 100%);
           -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hdr p { color:#778899; font-size:.95rem; letter-spacing:.28em; text-transform:uppercase; margin-top:.4rem; }
.card { background:linear-gradient(135deg,rgba(255,215,0,.04),rgba(255,140,0,.02)); border:1px solid rgba(255,215,0,.14); border-radius:14px; padding:1.8rem 2rem; margin:1.6rem 0; position:relative; }
.badge { position:absolute; top:-13px; left:20px; background:#FFD700; color:#000; font-family:'Cinzel',serif; font-weight:700; font-size:.7rem; letter-spacing:.2em; padding:3px 16px; border-radius:20px; }
.stButton>button { width:100%; background:linear-gradient(135deg,#FFD700,#FFA500); color:#000; font-family:'Rajdhani',sans-serif; font-weight:700; font-size:1.1rem; letter-spacing:.1em; border:none; border-radius:9px; height:3.4em; text-transform:uppercase; transition:all .2s; }
.stButton>button:hover { box-shadow:0 8px 28px rgba(255,215,0,.4); transform:translateY(-1px); }
.stTextInput>div>div>input { background:rgba(255,255,255,.04)!important; border:1px solid rgba(255,215,0,.22)!important; border-radius:8px!important; color:#fff!important; }
.mrow { display:flex; gap:.9rem; margin:1rem 0; flex-wrap:wrap; }
.mbox { flex:1; min-width:100px; background:rgba(255,215,0,.06); border:1px solid rgba(255,215,0,.18); border-radius:9px; padding:1rem; text-align:center; }
.mbox .v { font-family:'Cinzel',serif; font-size:1.9rem; color:#FFD700; font-weight:700; }
.mbox .l { font-size:.72rem; color:#556; text-transform:uppercase; letter-spacing:.15em; margin-top:.2rem; }
[data-testid="stSidebar"] { background:rgba(4,8,18,.95); border-right:1px solid rgba(255,215,0,.1); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hdr">
  <h1>🏥 GURJAS V10</h1>
  <p>Dr. Vasu Memorial Clinic &nbsp;·&nbsp; AI Cartoon Director &nbsp;·&nbsp; Industrial Grade</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# INIT
# ══════════════════════════════════════════════════════════════════════
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("🚨 GROQ_KEY missing in Streamlit Secrets! Add it and reboot.")
    st.stop()

PROJECT_DIR = "gurjas_v10_vault"

for k, v in [("package", ""), ("scenes", []), ("angles", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

def fresh_vault():
    if os.path.exists(PROJECT_DIR): shutil.rmtree(PROJECT_DIR)
    for d in ["img", "aud", "clips"]: os.makedirs(f"{PROJECT_DIR}/{d}")


# ══════════════════════════════════════════════════════════════════════
# ██████████████████  CARTOON ENGINE  ████████████████████████████████
# ══════════════════════════════════════════════════════════════════════

# Color palettes per medical category
PALETTES = {
    "heart":      [(220,50,50),  (255,100,80),  (180,20,20),  (255,200,180)],
    "brain":      [(80,50,180),  (140,90,220),  (50,20,150),  (200,170,255)],
    "lung":       [(50,150,220), (90,190,255),  (20,100,180), (180,230,255)],
    "blood":      [(200,30,30),  (255,80,60),   (150,0,0),    (255,180,160)],
    "diabetes":   [(50,180,100), (100,220,140), (20,130,60),  (180,255,200)],
    "bone":       [(200,170,120),(230,200,150), (160,130,80), (255,240,200)],
    "stomach":    [(220,140,50), (255,180,80),  (180,100,20), (255,220,160)],
    "kidney":     [(180,80,180), (220,120,220), (140,40,140), (255,200,255)],
    "liver":      [(160,100,40), (200,140,70),  (120,70,20),  (240,200,140)],
    "eye":        [(40,160,200), (80,200,240),  (20,120,160), (160,230,255)],
    "default":    [(30,120,200), (70,160,240),  (10,80,160),  (160,210,255)],
}

def get_palette(keyword: str):
    kw = keyword.lower()
    for cat in PALETTES:
        if cat in kw:
            return PALETTES[cat]
    if any(w in kw for w in ["attack","cardiac","chest","artery","vein"]): return PALETTES["heart"]
    if any(w in kw for w in ["stroke","neuro","memory","headache"]): return PALETTES["brain"]
    if any(w in kw for w in ["breath","oxygen","asthma","respiratory"]): return PALETTES["lung"]
    if any(w in kw for w in ["sugar","insulin","glucose"]): return PALETTES["diabetes"]
    return PALETTES["default"]


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))


def draw_gradient_bg(draw, W, H, pal):
    """Draw a rich multi-stop gradient background."""
    dark = tuple(max(0, c//4) for c in pal[0])
    mid  = tuple(c//2 for c in pal[1])
    for y in range(H):
        t = y / H
        if t < 0.5:
            c = lerp_color(dark, mid, t*2)
        else:
            c = lerp_color(mid, (10,10,30), (t-0.5)*2)
        draw.line([(0,y),(W,y)], fill=c)


def draw_glow_circle(img_draw_img, cx, cy, r, color, layers=8):
    """Soft glowing circle."""
    draw = img_draw_img
    for i in range(layers, 0, -1):
        alpha = int(40 * (i / layers))
        rad = r + (layers - i) * 18
        bbox = [cx-rad, cy-rad, cx+rad, cy+rad]
        draw.ellipse(bbox, fill=color + (alpha,) if len(color)==3 else color)


def draw_heart_scene(draw, W, H, pal):
    """Cartoon anatomical heart with pulse line."""
    cx, cy = W//2, H//2 - 80
    # Outer glow
    for g in range(10, 0, -1):
        r = 280 + g*20
        alpha_col = tuple(max(0,c-20) for c in pal[2])
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=alpha_col)
    # Heart body (two circles + triangle)
    r = 200
    draw.ellipse([cx-r-60, cy-r, cx+60, cy+60], fill=pal[0])
    draw.ellipse([cx-60, cy-r, cx+r+60, cy+60], fill=pal[0])
    draw.polygon([(cx-r-50,cy+20),(cx+r+50,cy+20),(cx,cy+r+100)], fill=pal[0])
    # Highlight
    draw.ellipse([cx-160,cy-160,cx-60,cy-80], fill=pal[3])
    # Pulse / ECG line
    pulse_y = cy + r + 180
    pts = []
    for x in range(50, W-50, 12):
        t = (x - 50) / (W-100)
        if 0.35 < t < 0.45:
            pts.append((x, pulse_y - int(math.sin((t-0.35)*math.pi/0.1)*180)))
        elif 0.45 < t < 0.55:
            pts.append((x, pulse_y + int(math.sin((t-0.45)*math.pi/0.1)*60)))
        else:
            pts.append((x, pulse_y))
    for i in range(len(pts)-1):
        draw.line([pts[i], pts[i+1]], fill=pal[3], width=7)
    # Plus symbols
    for px, py in [(120,300),(W-120,300),(120,H-300),(W-120,H-300)]:
        draw.rectangle([px-5, py-25, px+5, py+25], fill=pal[3])
        draw.rectangle([px-25, py-5, px+25, py+5], fill=pal[3])


def draw_brain_scene(draw, W, H, pal):
    """Cartoon brain with neural connections."""
    cx, cy = W//2, H//2 - 60
    # Glow
    for g in range(8, 0, -1):
        r = 260 + g*22
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=tuple(max(0,c//3) for c in pal[0]))
    # Left hemisphere
    draw.ellipse([cx-260, cy-220, cx+20, cy+200], fill=pal[0])
    # Right hemisphere
    draw.ellipse([cx-20, cy-220, cx+260, cy+200], fill=pal[1])
    # Cortex folds
    for i in range(6):
        angle = math.pi * i / 6
        x1 = cx + int(200*math.cos(angle)) - 30
        y1 = cy + int(180*math.sin(angle)) - 30
        draw.arc([x1,y1,x1+60,y1+60], 0, 180, fill=tuple(max(0,c-40) for c in pal[0]), width=8)
    # Neural connections
    nodes = [(cx-180,cy-80),(cx-60,cy-150),(cx+80,cy-100),(cx+180,cy+40),(cx-100,cy+120),(cx+40,cy+160),(cx-200,cy+60)]
    for i,n in enumerate(nodes):
        draw.ellipse([n[0]-18,n[1]-18,n[0]+18,n[1]+18], fill=pal[3])
        if i < len(nodes)-1:
            draw.line([n, nodes[(i+2)%len(nodes)]], fill=pal[3]+(150,) if len(pal[3])==4 else pal[3], width=4)


def draw_lung_scene(draw, W, H, pal):
    """Cartoon lungs with bronchial tree."""
    cx, cy = W//2, H//2 - 40
    # Left lung
    draw.ellipse([cx-300, cy-220, cx-20, cy+260], fill=pal[0])
    # Right lung
    draw.ellipse([cx+20, cy-220, cx+300, cy+260], fill=pal[1])
    # Trachea
    draw.rectangle([cx-22, cy-340, cx+22, cy-200], fill=pal[3])
    # Bronchi
    draw.line([(cx,cy-200),(cx-150,cy-80)], fill=pal[3], width=16)
    draw.line([(cx,cy-200),(cx+150,cy-80)], fill=pal[3], width=16)
    for side in [-1,1]:
        base_x = cx + side*150
        for branch in range(4):
            bx = base_x + side*branch*30
            by = cy - 80 + branch*60
            draw.line([(bx,by),(bx+side*40,by+50)], fill=pal[3], width=8)
            draw.line([(bx,by),(bx-side*20,by+50)], fill=pal[2], width=6)
    # Alveoli bubbles
    for bx,by in [(cx-180,cy+80),(cx-220,cy),(cx+180,cy+80),(cx+220,cy),(cx-160,cy+160),(cx+160,cy+160)]:
        draw.ellipse([bx-22,by-22,bx+22,by+22], fill=pal[3])


def draw_generic_medical(draw, W, H, pal, keyword):
    """Universal cartoon medical scene: DNA, pills, stethoscope elements."""
    cx, cy = W//2, H//2
    # Central circle
    for r in range(220, 0, -10):
        t = r/220
        c = lerp_color(pal[1], pal[0], t)
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=c)
    # Stethoscope curve
    pts = []
    for i in range(80):
        angle = math.pi * i / 40
        r = 180 + 40*math.sin(angle*3)
        pts.append((cx+int(r*math.cos(angle)), cy+int(r*math.sin(angle))))
    for i in range(len(pts)-1):
        draw.line([pts[i],pts[i+1]], fill=pal[3], width=9)
    # Cross symbol
    cw = 60
    draw.rectangle([cx-cw//4, cy-cw, cx+cw//4, cy+cw], fill=(255,255,255))
    draw.rectangle([cx-cw, cy-cw//4, cx+cw, cy+cw//4], fill=(255,255,255))
    # Orbiting dots
    for i in range(8):
        a = 2*math.pi*i/8
        ox, oy = cx+int(300*math.cos(a)), cy+int(300*math.sin(a))
        draw.ellipse([ox-16,oy-16,ox+16,oy+16], fill=pal[3])
        draw.line([(cx,cy),(ox,oy)], fill=pal[2], width=3)


def draw_warning_banner(draw, W, H, pal):
    """Decorative top + bottom accent bars with dots."""
    bar_h = 90
    for y in range(bar_h):
        t = y/bar_h
        c = lerp_color(pal[0], tuple(max(0,c-80) for c in pal[0]), t)
        draw.line([(0,y),(W,y)], fill=c)
        draw.line([(0,H-1-y),(W,H-1-y)], fill=c)
    # Dot row
    for x in range(40, W-40, 60):
        draw.ellipse([x-6,40,x+6,52], fill=pal[3])
        draw.ellipse([x-6,H-52,x+6,H-40], fill=pal[3])


def draw_scene_label(draw, W, H, keyword, pal):
    """Bold keyword label in upper area (using default font — no TTF needed)."""
    label = keyword.upper()[:28]
    # Background pill
    lw = len(label)*14 + 40
    lx = (W - lw)//2
    draw.rounded_rectangle([lx, 110, lx+lw, 160], radius=20, fill=tuple(max(0,c-60) for c in pal[0]))
    # Text using default PIL font (always available)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    draw.text(((W-len(label)*18)//2, 115), label, fill=pal[3], font=font)


def create_cartoon_frame(keyword: str, scene_idx: int, total_scenes: int, pal) -> Image.Image:
    """
    Master cartoon frame builder.
    Routes to the right illustration based on keyword.
    Returns a 1080×1920 PIL Image.
    """
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    draw_gradient_bg(draw, W, H, pal)
    draw_warning_banner(draw, W, H, pal)

    kw = keyword.lower()
    if any(w in kw for w in ["heart","cardiac","attack","chest","artery","coronary","blood pressure"]):
        draw_heart_scene(draw, W, H, pal)
    elif any(w in kw for w in ["brain","stroke","neuro","memory","nerve","alzheimer"]):
        draw_brain_scene(draw, W, H, pal)
    elif any(w in kw for w in ["lung","breath","respiratory","asthma","oxygen","pulmon"]):
        draw_lung_scene(draw, W, H, pal)
    else:
        draw_generic_medical(draw, W, H, pal, kw)

    draw_scene_label(draw, W, H, keyword, pal)

    # Scene number indicator bottom
    try:
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except Exception:
        font_sm = ImageFont.load_default()
    for dot_i in range(total_scenes):
        dot_x = W//2 - (total_scenes*24)//2 + dot_i*24 + 12
        dot_y = H - 60
        col = pal[3] if dot_i == scene_idx else tuple(max(0,c-120) for c in pal[3])
        draw.ellipse([dot_x-8, dot_y-8, dot_x+8, dot_y+8], fill=col)

    # Soft vignette via blur on edges
    blur_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    bd = ImageDraw.Draw(blur_layer)
    for i in range(60):
        alpha = int(180 * (i/60)**2)
        bd.rectangle([i, i, W-i, H-i], outline=(0,0,0,alpha), width=1)
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, blur_layer)
    return img.convert("RGB")


def generate_cartoon_image(keyword: str, idx: int, total: int) -> str:
    """Generate cartoon image and save to file. ALWAYS succeeds."""
    pal = get_palette(keyword)
    img = create_cartoon_frame(keyword, idx, total, pal)
    path = f"{PROJECT_DIR}/img/scene_{idx}.png"
    img.save(path, quality=95)
    return path


# ══════════════════════════════════════════════════════════════════════
# VOICE ENGINE
# ══════════════════════════════════════════════════════════════════════

async def tts_male(text: str, path: str):
    """hi-IN-MadhurNeural = deepest male Hindi voice. rate -10%, pitch -20Hz for authoritative tone."""
    await edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="-10%", pitch="-20Hz").save(path)


def get_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True
    )
    try: return max(float(r.stdout.strip()), 2.5)
    except: return 4.0


# ══════════════════════════════════════════════════════════════════════
# VIDEO ENGINE
# ══════════════════════════════════════════════════════════════════════

def image_to_ken_burns(img_path: str, dur: float, idx: int) -> str:
    """Ken Burns cinematic zoom — 3 alternating patterns for variety."""
    out = f"{PROJECT_DIR}/clips/kb_{idx}.ts"
    frames = max(int(dur * 25), 62)
    patterns = [
        ("min(zoom+0.0018,1.55)", "iw/2-(iw/zoom/2)",       "ih/2-(ih/zoom/2)"),
        ("if(eq(on,1),1.45,max(zoom-0.0015,1.0))", "iw/2-(iw/zoom/2)+on*0.25", "ih/3-(ih/zoom/3)"),
        ("min(zoom+0.0012,1.35)", "iw/3-(iw/zoom/3)+on*0.15","ih/2-(ih/zoom/2)"),
    ]
    z, x, y = patterns[idx % 3]
    cmd = (
        f'ffmpeg -y -loop 1 -i "{img_path}" '
        f'-vf "zoompan=z=\'{z}\':d={frames}:x=\'{x}\':y=\'{y}\':s=1080x1920:fps=25,scale=1080:1920" '
        f'-t {dur:.3f} -c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return out if (os.path.exists(out) and os.path.getsize(out) > 500) else None


def burn_subtitle(clip: str, text: str, idx: int) -> str:
    """Burn clean Hindi subtitle at bottom of frame."""
    out = f"{PROJECT_DIR}/clips/sub_{idx}.ts"
    safe = re.sub(r"[\"':\\%]", " ", text)[:72]
    cmd = (
        f'ffmpeg -y -i "{clip}" '
        f'-vf "drawtext=text=\'{safe}\':fontcolor=white:fontsize=44:'
        f'x=(w-text_w)/2:y=h-200:box=1:boxcolor=black@0.72:boxborderw=20" '
        f'-c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning'
    )
    subprocess.run(cmd, shell=True)
    return out if (os.path.exists(out) and os.path.getsize(out) > 500) else clip


def concat_ts(paths, out):
    lst = f"{PROJECT_DIR}/concat.txt"
    with open(lst,"w") as f:
        for p in paths: f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{out}" -loglevel warning', shell=True)


def concat_audio(paths, out):
    lst = f"{PROJECT_DIR}/alist.txt"
    with open(lst,"w") as f:
        for p in paths: f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{out}" -loglevel warning', shell=True)


def final_render(video, audio, output):
    """Mix + gold clinic brand bar + cinematic color grade."""
    cmd = (
        f'ffmpeg -y -i "{video}" -i "{audio}" '
        f'-filter_complex "'
        f'[0:v]vignette=PI/5[v1];'
        f'[v1]eq=contrast=1.12:brightness=0.03:saturation=1.2[v2];'
        f'[v2]drawbox=y=0:x=0:w=iw:h=110:color=black@0.88:t=fill[v3];'
        f'[v3]drawtext=text=\'DR. VASU MEMORIAL CLINIC\':'
        f'fontcolor=#FFD700:fontsize=42:x=(w-text_w)/2:y=32[final]" '
        f'-map "[final]" -map 1:a -c:v libx264 -preset fast '
        f'-c:a aac -b:a 192k -shortest -movflags +faststart "{output}" -loglevel warning'
    )
    subprocess.run(cmd, shell=True)


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR — IDEATION AGENT
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔬 IDEATION")
    broad = st.text_input("Medical Topic:", placeholder="e.g. Silent Heart Attack")
    num_scenes = st.slider("📽️ Scenes:", 4, 12, 6)
    add_subs = st.checkbox("📝 Hindi Subtitles", value=True)
    show_prev = st.checkbox("🖼️ Show Previews", value=True)

    if st.button("🔍 5 VIRAL ANGLES"):
        if broad.strip():
            with st.spinner("Analyzing..."):
                r = client.chat.completions.create(
                    messages=[{"role":"user","content":
                        f"Viral Hindi medical content strategist. Topic: {broad}. "
                        f"Give 5 shocking emotional video angles in Hindi (Devanagari). "
                        f"1 dramatic punchy line each. Numbered 1-5."}],
                    model="llama-3.3-70b-versatile", max_tokens=500
                )
                st.session_state.angles = r.choices[0].message.content
        else:
            st.warning("Enter a topic first.")

    if st.session_state.angles:
        st.info(st.session_state.angles)

    st.markdown("---")
    st.markdown("### 🛠️ Live Log")
    log = st.empty()


# ══════════════════════════════════════════════════════════════════════
# STAGE 1 — VIRAL CONTENT BRAIN
# ══════════════════════════════════════════════════════════════════════
st.markdown('<div class="card"><span class="badge">STAGE 1 — CONTENT BRAIN</span>', unsafe_allow_html=True)

topic = st.text_input(
    "💉 Medical Topic:",
    placeholder="e.g. 3 Silent Signs of Heart Attack jo doctor bhi miss kar dete hain"
)

if st.button("⚡ GENERATE COMPLETE VIRAL PACKAGE"):
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        with st.status("🧠 Building viral package...", expanded=True) as s:
            st.write(f"Generating {num_scenes}-scene script with image directions...")
            prompt = f"""You are the world's best viral Hindi medical content director.
TOPIC: {topic}

Generate a COMPLETE package:

[HOOK] — 1 shocking Hindi line to open the video. Creates fear or deep curiosity.
[CAPTION] — 3-4 emotional Hindi lines for Instagram caption. Include CTA.
[HASHTAGS] — 20 hashtags (Hindi + English medical).
[THUMBNAIL] — 3-5 bold Hindi words for thumbnail. Curiosity-gap.
[STORY] — 3-line emotional Hindi patient story.
[CTA] — "Dr. Vasu Memorial Clinic mein zaroor aayein."

[SCENES]
Write exactly {num_scenes} scene lines. STRICT FORMAT (one per line, no extra lines):
SCENE | <3-5 word English medical keyword for this scene> | <1-2 sentence authoritative Hindi dialogue for male doctor voice> | <scene_type: one of: heart / brain / lung / diabetes / general>

Example line:
SCENE | silent heart attack warning | Yeh teen khamoshi ke signs batate hain ki aapka dil khatre mein hai. | heart

All {num_scenes} scenes now:"""

            res = client.chat.completions.create(
                messages=[{"role":"user","content":prompt}],
                model="llama-3.3-70b-versatile", max_tokens=3500
            )
            raw = res.choices[0].message.content
            st.session_state.package = raw

            found = re.findall(
                r"SCENE\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\w+)\s*$",
                raw, re.MULTILINE
            )
            # Also try 3-column without type
            if len(found) < 2:
                found2 = re.findall(
                    r"SCENE\s*\|\s*(.+?)\s*\|\s*(.+?)(?:\s*\|\s*(\w+))?\s*$",
                    raw, re.MULTILINE
                )
                found = [(m[0],m[1],m[2] if m[2] else "general") for m in found2]

            st.session_state.scenes = [
                {"keyword": m[0].strip(), "hindi": m[1].strip(), "type": m[2].strip()}
                for m in found if m[0].strip() and m[1].strip()
            ]
            n = len(st.session_state.scenes)
            s.update(label=f"✅ {n} scenes ready!", state="complete")

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.package:
    with st.expander("📋 Full Viral Package — Review & Copy"):
        st.markdown(st.session_state.package)

    sc = st.session_state.scenes
    if sc:
        st.markdown(f"""
        <div class="mrow">
          <div class="mbox"><div class="v">{len(sc)}</div><div class="l">Scenes</div></div>
          <div class="mbox"><div class="v">♂</div><div class="l">Madhur Voice</div></div>
          <div class="mbox"><div class="v">🎨</div><div class="l">Cartoon PIL</div></div>
          <div class="mbox"><div class="v">₹0</div><div class="l">Total Cost</div></div>
        </div>""", unsafe_allow_html=True)

        with st.expander("🎬 Storyboard Preview"):
            for i, s in enumerate(sc):
                c1,c2,c3 = st.columns([1,2,1])
                c1.markdown(f"**Scene {i+1}**")
                c2.write(s["hindi"])
                c3.caption(f"🎨 `{s['type']}`\n\n`{s['keyword']}`")
                st.divider()


# ══════════════════════════════════════════════════════════════════════
# STAGE 2 — PRODUCTION ENGINE
# ══════════════════════════════════════════════════════════════════════
if st.session_state.scenes:
    st.markdown('<div class="card"><span class="badge">STAGE 2 — PRODUCTION ENGINE</span>', unsafe_allow_html=True)
    st.info("🎨 Cartoon illustrations generated by Python PIL — 100% offline, 100% relevant, 100% free.")

    if st.button("🎬 LAUNCH CARTOON VIDEO PRODUCTION"):
        fresh_vault()
        scenes = st.session_state.scenes
        total = len(scenes)
        prog = st.progress(0, text="Warming up engines...")
        clips, audios = [], []

        try:
            for idx, sc in enumerate(scenes):
                prog.progress(int(idx/total*78), text=f"⚙️ Scene {idx+1}/{total}: Cartoon + Voice...")

                # ── 1. CARTOON ILLUSTRATION (PIL — guaranteed, instant) ──
                log.write(f"🎨 Drawing cartoon: {sc['keyword']} ({sc['type']})...")
                img_path = generate_cartoon_image(sc["keyword"], idx, total)
                log.write(f"   ✅ Image: {img_path}")

                # ── 2. MALE VOICE TTS ────────────────────────────────────
                log.write(f"🎙️ Voice (Madhur): scene {idx+1}...")
                aud_path = f"{PROJECT_DIR}/aud/s{idx}.mp3"
                asyncio.run(tts_male(sc["hindi"], aud_path))
                dur = get_duration(aud_path)
                log.write(f"   ✅ Audio: {dur:.1f}s")

                # ── 3. KEN BURNS ANIMATION ───────────────────────────────
                log.write(f"🎥 Ken Burns animation...")
                clip = image_to_ken_burns(img_path, dur, idx)
                if clip is None:
                    log.write(f"   ⚠️ Animation failed for scene {idx+1}, skipping.")
                    continue

                # ── 4. BURN SUBTITLES ────────────────────────────────────
                if add_subs:
                    clip = burn_subtitle(clip, sc["hindi"], idx)

                clips.append(clip)
                audios.append(aud_path)

                # ── 5. PREVIEW ───────────────────────────────────────────
                if show_prev:
                    with st.expander(f"🖼️ Scene {idx+1} — {sc['keyword']}", expanded=False):
                        st.image(img_path, caption=f"🎨 {sc['keyword'].upper()} | {sc['hindi'][:50]}...")

                log.write(f"✅ Scene {idx+1} complete ({dur:.1f}s)")

            if not clips:
                st.error("❌ No scenes rendered. This should not happen — please report this error.")
                st.stop()

            # ── STITCH ───────────────────────────────────────────────────
            prog.progress(80, text="🔗 Stitching all cartoon scenes...")
            raw_vid = f"{PROJECT_DIR}/video_raw.mp4"
            concat_ts(clips, raw_vid)
            log.write("✅ Video stitched.")

            prog.progress(87, text="🔊 Merging voice tracks...")
            fin_aud = f"{PROJECT_DIR}/final_audio.mp3"
            concat_audio(audios, fin_aud)
            log.write("✅ Audio merged.")

            prog.progress(93, text="🎨 Cinematic grade + clinic branding...")
            output = f"DrVasu_V10_{int(time.time())}.mp4"
            final_render(raw_vid, fin_aud, output)
            log.write("✅ Final render done.")

            prog.progress(100, text="✅ Production complete!")

            # ── DELIVERY ─────────────────────────────────────────────────
            if os.path.exists(output) and os.path.getsize(output) > 10000:
                st.balloons()
                st.success("🏥 World-Class Cartoon Medical Video Ready!")
                st.video(output)
                with open(output,"rb") as f:
                    st.download_button("📥 DOWNLOAD VIDEO", f, file_name=output, mime="video/mp4")

                dur_total = sum(get_duration(a) for a in audios)
                size_mb = os.path.getsize(output)/1024/1024
                st.markdown(f"""
                <div class="mrow">
                  <div class="mbox"><div class="v">{len(clips)}</div><div class="l">Scenes</div></div>
                  <div class="mbox"><div class="v">{dur_total:.0f}s</div><div class="l">Duration</div></div>
                  <div class="mbox"><div class="v">{size_mb:.1f}MB</div><div class="l">File Size</div></div>
                  <div class="mbox"><div class="v">FREE</div><div class="l">Cost</div></div>
                </div>""", unsafe_allow_html=True)
            else:
                st.error("⚠️ Output file missing. Check logs.")

        except Exception as e:
            import traceback
            st.error(f"⚠️ Error: {e}")
            st.code(traceback.format_exc())

    st.markdown("</div>", unsafe_allow_html=True)
