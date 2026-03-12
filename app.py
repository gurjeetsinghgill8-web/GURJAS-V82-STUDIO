import streamlit as st
import os, asyncio, subprocess, shutil, re, time, math
import edge_tts
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title="GURJAS V11 | Suspense Studio", page_icon="🏥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Rajdhani:wght@400;600;700&display=swap');
.stApp{background:radial-gradient(ellipse at top,#080f1f 0%,#000308 70%);color:#e8e8e8;font-family:'Rajdhani',sans-serif;}
.hdr{text-align:center;padding:2.4rem 1rem 1.4rem;border-bottom:1px solid rgba(255,215,0,.18);margin-bottom:2rem;}
.hdr h1{font-family:'Cinzel',serif;font-size:2.7rem;font-weight:900;letter-spacing:.13em;
         background:linear-gradient(135deg,#FFD700 0%,#FFA500 50%,#FFD700 100%);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hdr p{color:#778899;font-size:.93rem;letter-spacing:.28em;text-transform:uppercase;margin-top:.4rem;}
.card{background:linear-gradient(135deg,rgba(255,215,0,.04),rgba(255,140,0,.02));
      border:1px solid rgba(255,215,0,.14);border-radius:14px;padding:1.8rem 2rem;margin:1.5rem 0;position:relative;}
.badge{position:absolute;top:-13px;left:20px;background:#FFD700;color:#000;
       font-family:'Cinzel',serif;font-weight:700;font-size:.69rem;letter-spacing:.2em;padding:3px 16px;border-radius:20px;}
.stButton>button{width:100%;background:linear-gradient(135deg,#FFD700,#FFA500);color:#000;
                 font-family:'Rajdhani',sans-serif;font-weight:700;font-size:1.1rem;
                 letter-spacing:.1em;border:none;border-radius:9px;height:3.4em;text-transform:uppercase;}
.stButton>button:hover{box-shadow:0 8px 28px rgba(255,215,0,.4);}
.stTextInput>div>div>input{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,215,0,.22)!important;border-radius:8px!important;color:#fff!important;}
.mrow{display:flex;gap:.9rem;margin:1rem 0;flex-wrap:wrap;}
.mbox{flex:1;min-width:90px;background:rgba(255,215,0,.06);border:1px solid rgba(255,215,0,.18);border-radius:9px;padding:1rem;text-align:center;}
.mbox .v{font-family:'Cinzel',serif;font-size:1.8rem;color:#FFD700;font-weight:700;}
.mbox .l{font-size:.7rem;color:#556;text-transform:uppercase;letter-spacing:.14em;margin-top:.2rem;}
.arc-row{display:flex;gap:6px;margin:.8rem 0;align-items:center;flex-wrap:wrap;}
.arc-step{padding:5px 14px;border-radius:20px;font-size:.78rem;font-weight:600;letter-spacing:.08em;font-family:'Rajdhani',sans-serif;}
[data-testid="stSidebar"]{background:rgba(3,6,14,.96);border-right:1px solid rgba(255,215,0,.1);}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hdr">
  <h1>🎬 GURJAS V11</h1>
  <p>Dr. Vasu Memorial Clinic &nbsp;·&nbsp; Suspense Story Engine &nbsp;·&nbsp; Cartoon Director</p>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────────────────────────
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("🚨 GROQ_KEY missing in Streamlit Secrets! Add it and reboot.")
    st.stop()

PROJECT_DIR = "gurjas_v11"

for k, v in [("package", ""), ("scenes", []), ("angles", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

def fresh():
    if os.path.exists(PROJECT_DIR):
        shutil.rmtree(PROJECT_DIR)
    for d in ["img", "aud", "clips"]:
        os.makedirs(f"{PROJECT_DIR}/{d}")

# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────
W, H = 1080, 1920

def lc(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def grad_bg(draw, top, bot):
    for y in range(H):
        draw.line([(0, y), (W, y)], fill=lc(top, bot, y / H))

def get_font(size=36):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

# ─────────────────────────────────────────────────────────────────
# MOOD PALETTES  (bg_top, bg_bot, accent, text_col)
# ─────────────────────────────────────────────────────────────────
MOODS = {
    "hook":       {"top": (30, 0, 0),    "bot": (8, 0, 0),    "ac": (255, 60,  60),  "tx": (255, 200, 200)},
    "mystery":    {"top": (10, 0, 35),   "bot": (2,  0, 10),  "ac": (140, 80,  255), "tx": (210, 180, 255)},
    "clue":       {"top": (0,  20, 45),  "bot": (0,  5,  15), "ac": (40,  160, 255), "tx": (180, 220, 255)},
    "rising":     {"top": (30, 15, 0),   "bot": (10, 5,  0),  "ac": (255, 160, 0),   "tx": (255, 230, 170)},
    "reveal":     {"top": (0,  35, 15),  "bot": (0,  10, 5),  "ac": (0,   220, 120), "tx": (180, 255, 210)},
    "resolution": {"top": (20, 18, 0),   "bot": (6,  5,  0),  "ac": (255, 215, 0),   "tx": (255, 240, 180)},
}

def get_mood(phase):
    return MOODS.get(phase, MOODS["clue"])

# ─────────────────────────────────────────────────────────────────
# 15 UNIQUE CARTOON SCENE DRAWERS
# ─────────────────────────────────────────────────────────────────

def draw_heart(draw, ac, tx):
    cx, cy = W // 2, H // 2 - 100
    for g in range(8, 0, -1):
        r = 260 + g * 24
        dark = tuple(max(0, c // 6) for c in ac)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dark)
    draw.ellipse([cx - 240, cy - 200, cx + 60,  cy + 80], fill=ac)
    draw.ellipse([cx - 60,  cy - 200, cx + 240, cy + 80], fill=ac)
    draw.polygon([(cx - 240, cy + 40), (cx + 240, cy + 40), (cx, cy + 260)], fill=ac)
    draw.ellipse([cx - 130, cy - 160, cx - 50, cy - 90], fill=tx)
    py = cy + 380
    pts = []
    for x in range(60, W - 60, 10):
        t = (x - 60) / (W - 120)
        if 0.38 < t < 0.48:
            oy = -int(math.sin((t - 0.38) * math.pi / 0.1) * 200)
        elif 0.48 < t < 0.55:
            oy = int(math.sin((t - 0.48) * math.pi / 0.1) * 70)
        else:
            oy = 0
        pts.append((x, py + oy))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=tx, width=8)

def draw_brain(draw, ac, tx):
    cx, cy = W // 2, H // 2 - 80
    dark = tuple(max(0, c // 4) for c in ac)
    draw.ellipse([cx - 260, cy - 220, cx + 20,  cy + 210], fill=ac)
    draw.ellipse([cx - 20,  cy - 220, cx + 260, cy + 210], fill=tuple(max(0, c - 40) for c in ac))
    for i in range(7):
        ang = math.pi * i / 7
        x1 = cx + int(190 * math.cos(ang)) - 25
        y1 = cy + int(170 * math.sin(ang)) - 25
        draw.arc([x1, y1, x1 + 50, y1 + 50], 0, 200, fill=tx, width=7)
    nodes = [(cx - 180, cy - 80), (cx - 60, cy - 150), (cx + 90, cy - 100),
             (cx + 190, cy + 50), (cx - 100, cy + 130), (cx + 50, cy + 170)]
    for i, n in enumerate(nodes):
        draw.ellipse([n[0] - 16, n[1] - 16, n[0] + 16, n[1] + 16], fill=tx)
        nxt = nodes[(i + 2) % len(nodes)]
        draw.line([n, nxt], fill=tx, width=4)

def draw_lungs(draw, ac, tx):
    cx, cy = W // 2, H // 2 - 40
    ac2 = tuple(max(0, c - 30) for c in ac)
    draw.ellipse([cx - 290, cy - 210, cx - 20, cy + 250], fill=ac)
    draw.ellipse([cx + 20,  cy - 210, cx + 290, cy + 250], fill=ac2)
    draw.rectangle([cx - 20, cy - 330, cx + 20, cy - 190], fill=tx)
    draw.line([(cx, cy - 190), (cx - 140, cy - 70)], fill=tx, width=14)
    draw.line([(cx, cy - 190), (cx + 140, cy - 70)], fill=tx, width=14)
    for s in [-1, 1]:
        bx = cx + s * 140
        for b in range(4):
            by = cy - 70 + b * 55
            draw.line([(bx + s * b * 20, by), (bx + s * (b * 20 + 50), by + 45)], fill=tx, width=7)

def draw_dna(draw, ac, tx):
    cx = W // 2
    for y in range(200, H - 200, 18):
        t = (y - 200) / (H - 400)
        ang = t * math.pi * 5
        x1 = cx + int(200 * math.cos(ang))
        x2 = cx + int(200 * math.cos(ang + math.pi))
        c1 = lc(ac, tx, abs(math.sin(ang)))
        c2 = lc(ac, tx, abs(math.cos(ang)))
        draw.ellipse([x1 - 18, y - 18, x1 + 18, y + 18], fill=c1)
        draw.ellipse([x2 - 18, y - 18, x2 + 18, y + 18], fill=c2)
        if y % 54 < 18:
            draw.line([(x1, y), (x2, y)], fill=tx, width=5)

def draw_blood_cells(draw, ac, tx):
    import random
    random.seed(42)
    for i in range(30):
        x = random.randint(80, W - 80)
        y = random.randint(300, H - 300)
        r = random.randint(28, 55)
        col = ac if i % 4 != 0 else (240, 240, 255)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)
        draw.ellipse([x - r // 2, y - r // 2, x + r // 2, y + r // 2],
                     fill=tuple(max(0, c - 60) for c in col))
    for fy in range(400, H - 300, 120):
        for fx in range(60, W - 60, 180):
            draw.polygon([(fx, fy), (fx + 30, fy - 20), (fx + 30, fy + 20)], fill=tx)

def draw_pill(draw, ac, tx):
    cx, cy = W // 2, H // 2 - 60
    draw.ellipse([cx - 180, cy - 80, cx + 20,  cy + 80], fill=ac)
    draw.ellipse([cx - 20,  cy - 80, cx + 180, cy + 80], fill=tx)
    draw.rectangle([cx - 20, cy - 80, cx + 20, cy + 80], fill=(200, 200, 220))
    for i in range(6):
        ang = 2 * math.pi * i / 6
        mx = cx + int(310 * math.cos(ang))
        my = cy + int(310 * math.sin(ang))
        draw.ellipse([mx - 22, my - 22, mx + 22, my + 22], fill=ac)
        draw.line([(mx, my), (cx + int(160 * math.cos(ang)), cy + int(160 * math.sin(ang)))],
                  fill=tx, width=5)

def draw_surgery(draw, ac, tx):
    cx, cy = W // 2, H // 2
    draw.rounded_rectangle([cx - 320, cy - 30,  cx + 320, cy + 50],  radius=20, fill=(60, 60, 80))
    draw.rounded_rectangle([cx - 280, cy - 80,  cx + 280, cy - 30],  radius=10, fill=(80, 80, 100))
    draw.ellipse([cx - 55, cy - 160, cx + 55, cy - 60], fill=(220, 180, 140))
    draw.rounded_rectangle([cx - 80, cy - 60, cx + 80, cy - 30], radius=8, fill=(220, 180, 140))
    draw.polygon([(cx, cy - 500), (cx - 160, cy - 120), (cx + 160, cy - 120)], fill=(255, 255, 200))
    draw.ellipse([cx - 30, cy - 530, cx + 30, cy - 470], fill=ac)
    for tx2, ty2 in [(cx - 220, cy + 100), (cx + 220, cy + 100),
                     (cx - 180, cy + 140), (cx + 180, cy + 140)]:
        draw.rectangle([tx2 - 8, ty2 - 50, tx2 + 8, ty2 + 50], fill=tx)
        draw.ellipse([tx2 - 12, ty2 - 60, tx2 + 12, ty2 - 40], fill=ac)

def draw_skeleton(draw, ac, tx):
    cx, cy = W // 2, H // 2 - 40
    draw.ellipse([cx - 90, cy - 300, cx + 90, cy - 140], fill=ac)
    draw.ellipse([cx - 50, cy - 170, cx + 50, cy - 140], fill=(5, 5, 15))
    draw.rectangle([cx - 25, cy - 140, cx + 25, cy - 110], fill=ac)
    for i in range(8):
        sy = cy - 100 + i * 55
        draw.rounded_rectangle([cx - 28, sy, cx + 28, sy + 40], radius=8, fill=ac)
    for side in [-1, 1]:
        for i in range(5):
            ry = cy - 60 + i * 45
            pts = [(cx + side * 28, ry), (cx + side * 160, ry - 15),
                   (cx + side * 170, ry + 20), (cx + side * 28, ry + 28)]
            draw.polygon(pts, fill=ac)
    draw.line([(cx - 28, cy - 80), (cx - 200, cy + 60), (cx - 180, cy + 220)], fill=ac, width=22)
    draw.line([(cx + 28, cy - 80), (cx + 200, cy + 60), (cx + 180, cy + 220)], fill=ac, width=22)

def draw_virus(draw, ac, tx):
    import random
    random.seed(7)
    cx, cy = W // 2, H // 2
    draw.ellipse([cx - 140, cy - 140, cx + 140, cy + 140], fill=(60, 120, 60))
    draw.ellipse([cx - 60,  cy - 60,  cx + 60,  cy + 60],  fill=(80, 160, 80))
    for i in range(12):
        vx = random.randint(60, W - 60)
        vy = random.randint(200, H - 200)
        if abs(vx - cx) < 200 and abs(vy - cy) < 200:
            vx += 220
        r = random.randint(30, 55)
        draw.ellipse([vx - r, vy - r, vx + r, vy + r], fill=ac)
        for sp in range(8):
            sa = 2 * math.pi * sp / 8
            draw.line(
                [(vx + int(r * math.cos(sa)), vy + int(r * math.sin(sa))),
                 (vx + int((r + 22) * math.cos(sa)), vy + int((r + 22) * math.sin(sa)))],
                fill=ac, width=5)

def draw_hospital(draw, ac, tx):
    draw.rectangle([0, H // 2, W, H], fill=(25, 25, 35))
    draw.rectangle([0, 0, W, H // 2], fill=(18, 18, 28))
    cx, cy = W // 2, H // 2
    draw.rounded_rectangle([80, cy - 60,  W - 80, cy + 180], radius=18, fill=(70, 70, 90))
    draw.rounded_rectangle([100, cy - 100, W - 100, cy - 60], radius=12, fill=(200, 180, 160))
    draw.rounded_rectangle([W - 340, cy - 320, W - 60, cy - 140], radius=14, fill=(20, 20, 30))
    draw.rectangle([W - 320, cy - 300, W - 80, cy - 160], fill=(0, 20, 0))
    pts = []
    py = cy - 230
    for x in range(W - 310, W - 90, 8):
        t = (x - (W - 310)) / 220
        oy = -int(math.sin((t - 0.4) * math.pi / 0.12) * 60) if 0.4 < t < 0.52 else 0
        pts.append((x, py + oy))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=(0, 255, 0), width=4)
    draw.ellipse([W - 520, cy - 400, W - 440, cy - 320], fill=tx)
    draw.line([(W - 480, cy - 320), (W - 480, cy - 60)], fill=tx, width=5)

def draw_warning(draw, ac, tx):
    cx, cy = W // 2, H // 2
    draw.polygon([(cx, cy - 340), (cx - 300, cy + 160), (cx + 300, cy + 160)], fill=ac)
    bg_col = (8, 8, 20)
    draw.polygon([(cx, cy - 270), (cx - 240, cy + 120), (cx + 240, cy + 120)], fill=bg_col)
    draw.rectangle([cx - 22, cy - 180, cx + 22, cy + 30], fill=ac)
    draw.ellipse([cx - 24, cy + 55, cx + 24, cy + 105], fill=ac)
    for ex, ey in [(140, 340), (W - 140, 340), (140, H - 340), (W - 140, H - 340)]:
        draw.rectangle([ex - 10, ey - 50, ex + 10, ey + 20], fill=ac)
        draw.ellipse([ex - 12, ey + 35, ex + 12, ey + 65], fill=ac)

def draw_microscope(draw, ac, tx):
    cx, cy = W // 2, H // 2
    draw.rectangle([cx - 25, cy - 320, cx + 25, cy + 40], fill=ac)
    draw.rectangle([cx - 80, cy - 360, cx + 80, cy - 300], fill=ac)
    draw.ellipse([cx - 40, cy - 380, cx + 40, cy - 300], fill=tx)
    draw.line([(cx, cy + 40), (cx - 130, cy + 200), (cx + 130, cy + 200)], fill=ac, width=30)
    draw.ellipse([cx - 220, cy - 260, cx + 220, cy + 180], fill=(10, 30, 10))
    for bx, by, br in [(cx - 60, cy - 80, 38), (cx + 70, cy - 40, 30),
                       (cx - 30, cy + 80, 45), (cx + 100, cy + 90, 28)]:
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(50, 200, 80))
        draw.ellipse([bx - br // 2, by - br // 2, bx + br // 2, by + br // 2], fill=(30, 150, 50))

def draw_xray(draw, ac, tx):
    cx, cy = W // 2, H // 2 - 60
    draw.rectangle([cx - 280, cy - 360, cx + 280, cy + 360], fill=(8, 8, 20))
    for i in range(6):
        ry = cy - 200 + i * 70
        for s in [-1, 1]:
            pts = [(cx + s * 30, ry), (cx + s * 220, ry - 20),
                   (cx + s * 230, ry + 35), (cx + s * 30, ry + 50)]
            draw.polygon(pts, fill=ac)
    for i in range(12):
        sy = cy - 220 + i * 45
        draw.rounded_rectangle([cx - 18, sy, cx + 18, sy + 32], radius=6, fill=tx)
    draw.ellipse([cx - 80, cy - 150, cx + 10, cy - 50], fill=(200, 50, 50))
    draw.ellipse([cx - 10, cy - 150, cx + 80, cy - 50], fill=(180, 40, 40))

def draw_injection(draw, ac, tx):
    cx, cy = W // 2, H // 2
    pts = [(cx - 200, cy - 40), (cx + 180, cy - 40), (cx + 200, cy), (cx + 180, cy + 40), (cx - 200, cy + 40)]
    draw.polygon(pts, fill=(200, 200, 220))
    draw.rectangle([cx - 200, cy - 20, cx - 160, cy + 20], fill=(160, 160, 180))
    draw.polygon([(cx + 200, cy - 8), (cx + 330, cy), (cx + 200, cy + 8)], fill=tx)
    draw.rectangle([cx - 190, cy - 28, cx - 40, cy + 28], fill=ac)
    draw.rectangle([cx - 220, cy - 40, cx - 200, cy + 40], fill=ac)
    for i in range(5):
        ang = 2 * math.pi * i / 5
        mx = cx + int(260 * math.cos(ang))
        my = cy + int(260 * math.sin(ang))
        draw.ellipse([mx - 18, my - 18, mx + 18, my + 18], fill=ac)

def draw_detective(draw, ac, tx):
    cx, cy = W // 2, H // 2 - 60
    for qx, qy in [(160, 300), (W - 160, 300), (200, H - 350), (W - 200, H - 350), (cx, 220)]:
        dim = tuple(c // 4 for c in ac)
        draw.arc([qx - 35, qy - 50, qx + 35, qy + 20], 200, 400, fill=dim, width=8)
        draw.ellipse([qx - 6, qy + 30, qx + 6, qy + 46], fill=dim)
    draw.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(20, 25, 40))
    draw.ellipse([cx - 180, cy - 180, cx + 180, cy + 180], fill=(10, 15, 25))
    draw.ellipse([cx - 80, cy - 80, cx + 10, cy + 10], fill=(220, 50, 50))
    draw.ellipse([cx - 10, cy - 80, cx + 80, cy + 10], fill=(200, 40, 40))
    draw.polygon([(cx - 80, cy - 20), (cx + 80, cy - 20), (cx, cy + 80)], fill=(210, 45, 45))
    draw.line([(cx + 190, cy + 190), (cx + 340, cy + 340)], fill=tx, width=30)
    draw.ellipse([cx + 310, cy + 310, cx + 370, cy + 370], fill=ac)

def draw_reveal(draw, ac, tx):
    cx, cy = W // 2, H // 2 - 80
    for i in range(24):
        ang = 2 * math.pi * i / 24
        x1 = cx + int(80 * math.cos(ang))
        y1 = cy + int(80 * math.sin(ang))
        x2 = cx + int(460 * math.cos(ang))
        y2 = cy + int(460 * math.sin(ang))
        bright = tuple(min(255, c + 50) for c in ac)
        draw.line([(x1, y1), (x2, y2)], fill=bright, width=8 if i % 2 == 0 else 4)
    for r in [220, 180, 140, 100, 60]:
        t = 1 - r / 220
        c = lc(ac, tx, t)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    draw.line([(cx - 60, cy), (cx - 10, cy + 60), (cx + 80, cy - 60)], fill=(255, 255, 255), width=18)


# Map name → function
SCENE_DRAWERS = {
    "heart":       draw_heart,
    "brain":       draw_brain,
    "lungs":       draw_lungs,
    "dna":         draw_dna,
    "blood_cells": draw_blood_cells,
    "pill":        draw_pill,
    "surgery":     draw_surgery,
    "skeleton":    draw_skeleton,
    "virus":       draw_virus,
    "hospital":    draw_hospital,
    "warning":     draw_warning,
    "microscope":  draw_microscope,
    "xray":        draw_xray,
    "injection":   draw_injection,
    "detective":   draw_detective,
    "reveal":      draw_reveal,
}

# Cycle order — ensures no two adjacent scenes look the same
CYCLE_ORDER = ["heart","brain","lungs","dna","blood_cells","pill","surgery",
               "skeleton","virus","hospital","warning","microscope","xray","injection","detective","reveal"]

def pick_scene(keyword, phase, idx):
    kw = keyword.lower()
    if any(w in kw for w in ["heart","cardiac","attack","chest","coronary","artery"]): return "heart"
    if any(w in kw for w in ["brain","stroke","neuro","memory","headache","migraine"]): return "brain"
    if any(w in kw for w in ["lung","breath","asthma","oxygen","respiratory"]):         return "lungs"
    if any(w in kw for w in ["dna","gene","cancer","tumor","chromosome"]):              return "dna"
    if any(w in kw for w in ["blood","cell","hemoglobin","anemia","clot"]):             return "blood_cells"
    if any(w in kw for w in ["medicine","pill","drug","tablet","treatment","dose"]):    return "pill"
    if any(w in kw for w in ["surgery","operation","bypass","transplant"]):             return "surgery"
    if any(w in kw for w in ["bone","joint","fracture","calcium","osteo"]):             return "skeleton"
    if any(w in kw for w in ["virus","bacteria","infection","fever","immune","covid"]): return "virus"
    if any(w in kw for w in ["hospital","ward","icu","patient","bed","admit"]):         return "hospital"
    if any(w in kw for w in ["warning","sign","symptom","danger","risk","alert"]):      return "warning"
    if any(w in kw for w in ["test","lab","biopsy","pathology","diagnosis"]):           return "microscope"
    if any(w in kw for w in ["xray","scan","mri","ct","imaging"]):                      return "xray"
    if any(w in kw for w in ["inject","vaccine","insulin","iv","syringe"]):             return "injection"
    # Phase fallback
    phase_map = {"hook":"warning","mystery":"detective","clue":"microscope",
                 "rising":"xray","reveal":"reveal","resolution":"hospital"}
    if phase in phase_map:
        return phase_map[phase]
    # Index cycle fallback — guarantees variety
    return CYCLE_ORDER[idx % len(CYCLE_ORDER)]


def build_frame(keyword, phase, idx, total):
    mood  = get_mood(phase)
    stype = pick_scene(keyword, phase, idx)
    fn    = SCENE_DRAWERS.get(stype, draw_warning)

    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    grad_bg(draw, mood["top"], mood["bot"])
    fn(draw, mood["ac"], mood["tx"])

    # Top phase bar
    bar_colors = {
        "hook": (70,0,0), "mystery": (25,0,70), "clue": (0,25,70),
        "rising": (70,35,0), "reveal": (0,55,25), "resolution": (55,45,0)
    }
    draw.rectangle([0, 0, W, 112], fill=bar_colors.get(phase, (20, 20, 50)))

    phase_labels = {
        "hook": "HOOK  —  DANGER", "mystery": "MYSTERY  —  SUSPENSE",
        "clue": "CLUE  —  EVIDENCE", "rising": "RISING  —  TENSION",
        "reveal": "REVEAL  —  THE TRUTH", "resolution": "RESOLUTION  —  SOLUTION"
    }
    label = phase_labels.get(phase, phase.upper())
    f = get_font(38)
    try:
        bb = draw.textbbox((0, 0), label, font=f)
        tw = bb[2] - bb[0]
    except Exception:
        tw = len(label) * 20
    draw.text(((W - tw) // 2, 33), label, fill=mood["ac"], font=f)

    # Bottom keyword bar
    draw.rectangle([0, H - 130, W, H], fill=tuple(max(0, c // 5) for c in mood["ac"]))
    kw_disp = keyword.upper()[:32]
    f2 = get_font(32)
    try:
        bb2 = draw.textbbox((0, 0), kw_disp, font=f2)
        tw2 = bb2[2] - bb2[0]
    except Exception:
        tw2 = len(kw_disp) * 17
    draw.text(((W - tw2) // 2, H - 105), kw_disp, fill=mood["tx"], font=f2)

    # Progress dots
    for d in range(total):
        dx = W // 2 - (total * 28) // 2 + d * 28 + 14
        col = mood["ac"] if d == idx else (40, 40, 60)
        draw.ellipse([dx - 9, H - 48 - 9, dx + 9, H - 48 + 9], fill=col)

    # Vignette
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(80):
        alpha = int(170 * (i / 80) ** 1.8)
        vd.rectangle([i, i, W - i, H - i], outline=(0, 0, 0, alpha), width=1)
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, vig).convert("RGB")

    path = f"{PROJECT_DIR}/img/s{idx}_{stype}.png"
    img.save(path)
    return path


# ─────────────────────────────────────────────────────────────────
# VOICE  (1.5x speed, deep male)
# ─────────────────────────────────────────────────────────────────
async def tts(text, path):
    await edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+50%", pitch="-12Hz").save(path)

def get_dur(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return max(float(r.stdout.strip()), 2.0)
    except Exception:
        return 3.5


# ─────────────────────────────────────────────────────────────────
# VIDEO ENGINE
# ─────────────────────────────────────────────────────────────────
def ken_burns(img, dur, idx):
    out = f"{PROJECT_DIR}/clips/kb_{idx}.ts"
    frames = max(int(dur * 25), 55)
    patterns = [
        ("min(zoom+0.0020,1.60)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
        ("if(eq(on,1),1.50,max(zoom-0.0018,1.0))", "iw/2-(iw/zoom/2)+on*0.28", "ih/3-(ih/zoom/3)"),
        ("min(zoom+0.0014,1.38)", "iw/3-(iw/zoom/3)+on*0.18", "ih/2-(ih/zoom/2)"),
        ("if(eq(on,1),1.45,max(zoom-0.0012,1.0))", "iw*2/3-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ]
    z, x, y = patterns[idx % 4]
    cmd = (
        f'ffmpeg -y -loop 1 -i "{img}" '
        f'-vf "zoompan=z=\'{z}\':d={frames}:x=\'{x}\':y=\'{y}\':s=1080x1920:fps=25,scale=1080:1920" '
        f'-t {dur:.3f} -c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning'
    )
    subprocess.run(cmd, shell=True)
    return out if (os.path.exists(out) and os.path.getsize(out) > 500) else None

def burn_sub(clip, text, idx):
    out = f"{PROJECT_DIR}/clips/sub_{idx}.ts"
    safe = re.sub(r'[\"\':\\%<>]', ' ', text)[:70]
    cmd = (
        f'ffmpeg -y -i "{clip}" '
        f'-vf "drawtext=text=\'{safe}\':fontcolor=white:fontsize=42:'
        f'x=(w-text_w)/2:y=h-210:box=1:boxcolor=black@0.75:boxborderw=20" '
        f'-c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning'
    )
    subprocess.run(cmd, shell=True)
    return out if (os.path.exists(out) and os.path.getsize(out) > 500) else clip

def concat_ts(paths, out):
    lst = f"{PROJECT_DIR}/concat.txt"
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{out}" -loglevel warning', shell=True)

def concat_aud(paths, out):
    lst = f"{PROJECT_DIR}/alist.txt"
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{out}" -loglevel warning', shell=True)

def final_render(vid, aud, out):
    cmd = (
        f'ffmpeg -y -i "{vid}" -i "{aud}" '
        f'-filter_complex "'
        f'[0:v]vignette=PI/5[v1];'
        f'[v1]eq=contrast=1.12:brightness=0.03:saturation=1.2[v2];'
        f'[v2]drawbox=y=0:x=0:w=iw:h=112:color=black@0.9:t=fill[v3];'
        f'[v3]drawtext=text=\'DR. VASU MEMORIAL CLINIC\':'
        f'fontcolor=#FFD700:fontsize=42:x=(w-text_w)/2:y=33[vf]" '
        f'-map "[vf]" -map 1:a -c:v libx264 -preset fast '
        f'-c:a aac -b:a 192k -shortest -movflags +faststart "{out}" -loglevel warning'
    )
    subprocess.run(cmd, shell=True)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
PHASE_EMOJI = {
    "hook": "🔴", "mystery": "🟣", "clue": "🔵",
    "rising": "🟠", "reveal": "🟢", "resolution": "🏆"
}

with st.sidebar:
    st.markdown("### 🔬 IDEATION AGENT")
    broad = st.text_input("Medical Topic:", placeholder="e.g. Silent Heart Attack")
    num_scenes = st.slider("📽️ Scenes:", 5, 12, 7)
    add_subs = st.checkbox("📝 Hindi Subtitles", True)
    show_prev = st.checkbox("🖼️ Show Previews", True)

    if st.button("🔍 5 VIRAL ANGLES"):
        if broad.strip():
            with st.spinner("Analyzing..."):
                r = client.chat.completions.create(
                    messages=[{"role": "user", "content":
                        f"Viral Hindi medical content strategist. Topic: {broad}. "
                        f"5 shocking suspense-style video angles in Hindi (Devanagari). "
                        f"Each: 1 dramatic line. Numbered 1-5. Sound like a thriller."}],
                    model="llama-3.3-70b-versatile", max_tokens=450)
                st.session_state.angles = r.choices[0].message.content
        else:
            st.warning("Enter a topic.")

    if st.session_state.angles:
        st.info(st.session_state.angles)

    st.markdown("---")
    st.markdown("### 🛠️ Live Logs")
    logbox = st.empty()


# ─────────────────────────────────────────────────────────────────
# STAGE 1 — SUSPENSE STORY GENERATOR
# ─────────────────────────────────────────────────────────────────
st.markdown('<div class="card"><span class="badge">STAGE 1 — SUSPENSE STORY ENGINE</span>', unsafe_allow_html=True)

st.markdown("""
<div class="arc-row">
  <div class="arc-step" style="background:#4a0000;color:#ff9999;">🔴 HOOK</div>
  <div style="color:#555">→</div>
  <div class="arc-step" style="background:#1a0040;color:#bb99ff;">🟣 MYSTERY</div>
  <div style="color:#555">→</div>
  <div class="arc-step" style="background:#001840;color:#99ccff;">🔵 CLUE</div>
  <div style="color:#555">→</div>
  <div class="arc-step" style="background:#402000;color:#ffcc88;">🟠 RISING</div>
  <div style="color:#555">→</div>
  <div class="arc-step" style="background:#004020;color:#88ffcc;">🟢 REVEAL</div>
  <div style="color:#555">→</div>
  <div class="arc-step" style="background:#302000;color:#FFD700;">🏆 RESOLUTION</div>
</div>
""", unsafe_allow_html=True)

topic = st.text_input(
    "💉 Medical Topic:",
    placeholder="e.g. Silent Heart Attack ke 3 signs jo sab ignore kar dete hain"
)

if st.button("⚡ GENERATE SUSPENSE STORY PACKAGE"):
    if not topic.strip():
        st.warning("Enter a topic.")
    else:
        with st.status("🧠 Writing suspense story arc...", expanded=True) as status:
            st.write("Building: hook → mystery → clues → big reveal → resolution...")

            # Build phase distribution
            if num_scenes <= 5:
                phase_list = ["hook", "mystery", "clue", "reveal", "resolution"][:num_scenes]
            elif num_scenes == 6:
                phase_list = ["hook", "mystery", "clue", "clue", "reveal", "resolution"]
            elif num_scenes == 7:
                phase_list = ["hook", "mystery", "clue", "rising", "clue", "reveal", "resolution"]
            elif num_scenes == 8:
                phase_list = ["hook", "mystery", "clue", "rising", "clue", "rising", "reveal", "resolution"]
            else:
                base = ["hook", "mystery", "clue", "rising", "clue", "rising", "clue", "reveal", "reveal", "resolution"]
                extras = ["rising", "clue"] * 10
                full = base + extras
                phase_list = full[:num_scenes]

            phases_str = "\n".join([f"Scene {i+1}: {p.upper()}" for i, p in enumerate(phase_list)])

            prompt = f"""You are the world's best medical thriller storyteller and viral Hindi content director.
TOPIC: {topic}

Write a SUSPENSE STORY video that keeps the viewer glued start to finish.

Story structure to follow:
{phases_str}

Phase rules:
- HOOK: Shocking fact or scary question. Viewer freezes. Instant fear/curiosity.
- MYSTERY: Something is wrong but we don't know what yet. Build dread.
- CLUE: Drop one clue at a time. Never reveal the full answer yet.
- RISING: Tension peaks. Viewer thinks they know but needs confirmation.
- REVEAL: THE BIG DRAMATIC TRUTH. The answer everyone was waiting for.
- RESOLUTION: Doctor's expert advice. Hope. Call to action.

STRICT SCENE FORMAT (one per line, no extra text):
SCENE | <phase name> | <3-5 word English medical keyword> | <1-2 authoritative Hindi sentences matching that phase mood>

Also include:
[HOOK_LINE] 5-word viral Hindi opening
[CAPTION] 3-4 emotional Hindi lines
[HASHTAGS] 20 hashtags
[THUMBNAIL] 4 bold Hindi words

Write all {num_scenes} SCENE lines now:"""

            res = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                max_tokens=4000
            )
            raw = res.choices[0].message.content
            st.session_state.package = raw

            # Parse scenes
            found = re.findall(
                r"SCENE\s*\|\s*(\w+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$",
                raw, re.MULTILINE
            )
            if len(found) < 2:
                # Fallback: 2-column (no phase)
                found2 = re.findall(r"SCENE\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$", raw, re.MULTILINE)
                found = [
                    (phase_list[i] if i < len(phase_list) else "clue", m[0], m[1])
                    for i, m in enumerate(found2)
                ]

            st.session_state.scenes = [
                {
                    "phase":   m[0].strip().lower(),
                    "keyword": m[1].strip(),
                    "hindi":   m[2].strip()
                }
                for m in found if m[1].strip() and m[2].strip()
            ]
            n = len(st.session_state.scenes)
            status.update(label=f"✅ {n}-scene suspense story ready!", state="complete")

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.package:
    with st.expander("📋 Full Package — Review & Copy"):
        st.markdown(st.session_state.package)

    sc = st.session_state.scenes
    if sc:
        st.markdown(f"""
        <div class="mrow">
          <div class="mbox"><div class="v">{len(sc)}</div><div class="l">Scenes</div></div>
          <div class="mbox"><div class="v">1.5x</div><div class="l">Voice Speed</div></div>
          <div class="mbox"><div class="v">15</div><div class="l">Cartoon Types</div></div>
          <div class="mbox"><div class="v">₹0</div><div class="l">Total Cost</div></div>
        </div>""", unsafe_allow_html=True)

        with st.expander("🎬 Story Arc Preview"):
            for i, s in enumerate(sc):
                emoji = PHASE_EMOJI.get(s["phase"], "⚪")
                c1, c2, c3 = st.columns([1, 1, 3])
                c1.markdown(f"**{i+1}**")
                c2.markdown(emoji + " `" + s["phase"] + "`")
                c3.write(s["hindi"])
                st.divider()


# ─────────────────────────────────────────────────────────────────
# STAGE 2 — PRODUCTION ENGINE
# ─────────────────────────────────────────────────────────────────
if st.session_state.scenes:
    st.markdown('<div class="card"><span class="badge">STAGE 2 — CARTOON PRODUCTION ENGINE</span>', unsafe_allow_html=True)
    st.info("🎨 15 unique cartoon types · 🎙️ 1.5x Male voice · 🎥 Ken Burns · 📝 Hindi subtitles")

    if st.button("🎬 LAUNCH SUSPENSE VIDEO PRODUCTION"):
        fresh()
        scenes = st.session_state.scenes
        total = len(scenes)
        prog = st.progress(0, text="Warming up engines...")
        clips, audios = [], []

        try:
            for idx, sc in enumerate(scenes):
                pct = int(idx / total * 78)
                prog.progress(pct, text=f"⚙️ Scene {idx+1}/{total}: {sc['phase'].upper()}...")

                # 1. Unique cartoon frame
                emoji = PHASE_EMOJI.get(sc["phase"], "⚪")
                logbox.write(f"🎨 {emoji} Drawing [{sc['phase']}]: {sc['keyword']}...")
                img_path = build_frame(sc["keyword"], sc["phase"], idx, total)
                logbox.write(f"   ✅ Cartoon saved.")

                # 2. 1.5x deep male voice
                logbox.write(f"🎙️ Voice 1.5x: {sc['hindi'][:40]}...")
                aud_path = f"{PROJECT_DIR}/aud/s{idx}.mp3"
                asyncio.run(tts(sc["hindi"], aud_path))
                dur = get_dur(aud_path)
                logbox.write(f"   ✅ {dur:.1f}s audio done.")

                # 3. Ken Burns animation
                clip = ken_burns(img_path, dur, idx)
                if clip is None:
                    logbox.write(f"   ⚠️ Animation failed scene {idx+1}, skipping.")
                    continue

                # 4. Subtitles
                if add_subs:
                    clip = burn_sub(clip, sc["hindi"], idx)

                clips.append(clip)
                audios.append(aud_path)

                # 5. Preview (FIX: emoji computed outside f-string)
                if show_prev:
                    title = emoji + " Scene " + str(idx + 1) + " — " + sc["keyword"]
                    with st.expander(title, expanded=False):
                        st.image(img_path, caption=sc["hindi"][:60])

                logbox.write(f"✅ Scene {idx+1} complete.")

            if not clips:
                st.error("❌ No clips produced. Please try again.")
                st.stop()

            prog.progress(80, text="🔗 Stitching story together...")
            raw_vid = f"{PROJECT_DIR}/video_raw.mp4"
            concat_ts(clips, raw_vid)
            logbox.write("✅ Video stitched.")

            prog.progress(87, text="🔊 Merging voice tracks...")
            fin_aud = f"{PROJECT_DIR}/final_audio.mp3"
            concat_aud(audios, fin_aud)
            logbox.write("✅ Audio merged.")

            prog.progress(93, text="🎨 Applying grade + clinic branding...")
            output = "DrVasu_SuspenseV11_" + str(int(time.time())) + ".mp4"
            final_render(raw_vid, fin_aud, output)
            logbox.write("✅ Final render done.")

            prog.progress(100, text="✅ Production complete!")

            if os.path.exists(output) and os.path.getsize(output) > 10000:
                st.balloons()
                st.success("🏥 Suspense Medical Video Ready — Hook to Resolution!")
                st.video(output)
                with open(output, "rb") as f:
                    st.download_button("📥 DOWNLOAD VIDEO", f, file_name=output, mime="video/mp4")

                dur_t = sum(get_dur(a) for a in audios)
                size  = os.path.getsize(output) / 1024 / 1024
                st.markdown(f"""
                <div class="mrow">
                  <div class="mbox"><div class="v">{len(clips)}</div><div class="l">Scenes</div></div>
                  <div class="mbox"><div class="v">{dur_t:.0f}s</div><div class="l">Duration</div></div>
                  <div class="mbox"><div class="v">{size:.1f}MB</div><div class="l">Size</div></div>
                  <div class="mbox"><div class="v">FREE</div><div class="l">Cost</div></div>
                </div>""", unsafe_allow_html=True)
            else:
                st.error("⚠️ Output file missing or empty. Check logs above.")

        except Exception as e:
            import traceback
            st.error(f"⚠️ Error: {e}")
            st.code(traceback.format_exc())

    st.markdown("</div>", unsafe_allow_html=True)
