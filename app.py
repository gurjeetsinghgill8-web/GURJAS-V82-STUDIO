"""
╔══════════════════════════════════════════════════════════════════════════╗
║  GURJAS V13 — DR. VASU COMPLETE CONTENT FACTORY                        ║
║                                                                          ║
║  NEW IN V13:                                                             ║
║  • Supervisor Agent  — quality check, story protection, keywords        ║
║  • Cartoon Doctor    — human doctor mascot on every scene               ║
║  • Multi-Clinic      — custom branding plate bottom-left                ║
║  • Full ZIP Package  — video + thumbnails + content + branding          ║
║  • Timestamped Folder— auto-organized output                            ║
║  • Auto Download     — ZIP triggers automatically on completion         ║
║  • Keep-Alive        — app stays alive during production                ║
║  • User Story Guard  — your story = enhanced, not replaced              ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os, asyncio, subprocess, shutil, re, time, math, zipfile
from datetime import datetime
import edge_tts
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GURJAS V13 | Dr. Vasu Factory",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
.stTextInput>div>div>input,.stTextArea>div>div>textarea{
    background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,215,0,.22)!important;
    border-radius:8px!important;color:#fff!important;}
.mrow{display:flex;gap:.9rem;margin:1rem 0;flex-wrap:wrap;}
.mbox{flex:1;min-width:90px;background:rgba(255,215,0,.06);border:1px solid rgba(255,215,0,.18);
      border-radius:9px;padding:1rem;text-align:center;}
.mbox .v{font-family:'Cinzel',serif;font-size:1.8rem;color:#FFD700;font-weight:700;}
.mbox .l{font-size:.7rem;color:#556;text-transform:uppercase;letter-spacing:.14em;margin-top:.2rem;}
.arc-row{display:flex;gap:6px;margin:.8rem 0;align-items:center;flex-wrap:wrap;}
.arc-step{padding:5px 14px;border-radius:20px;font-size:.78rem;font-weight:600;}
[data-testid="stSidebar"]{background:rgba(3,6,14,.96);border-right:1px solid rgba(255,215,0,.1);}
.agent-box{background:rgba(0,80,40,.15);border:1px solid rgba(0,200,100,.25);
           border-radius:10px;padding:1rem 1.2rem;margin:.6rem 0;font-size:.92rem;}
.brand-preview{background:rgba(20,15,0,.8);border:1px solid rgba(255,215,0,.3);
               border-radius:8px;padding:.8rem 1rem;margin:.4rem 0;font-size:.85rem;
               font-family:'Rajdhani',sans-serif;color:#FFD700;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hdr">
  <h1>🏥 GURJAS V13</h1>
  <p>Dr. Vasu Content Factory &nbsp;·&nbsp; Supervisor Agent &nbsp;·&nbsp; Full Package Studio</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════════════════════════════
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("🚨 GROQ_KEY missing in Streamlit Secrets!")
    st.stop()

PROJECT_BASE = "gurjas_output"

DEFAULTS = {
    "package": "", "scenes": [], "angles": "", "raw_llm": "",
    "supervised": {}, "production_running": False, "output_zip": "",
    "clinic_name": "Vasu Memorial Clinic",
    "doctor_name": "Dr. Vasu",
    "address1": "Vasudeva Complex",
    "address2": "Near Agrasen Park, Govindpuri",
    "address3": "Modinagar",
    "phone": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def make_project_folder(topic_slug):
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = re.sub(r'[^a-zA-Z0-9]', '_', topic_slug)[:20]
    folder = os.path.join(PROJECT_BASE, f"{slug}_{ts}")
    for sub in ["video", "thumbnails", "frames", "content", "branding", "audio", "clips"]:
        os.makedirs(os.path.join(folder, sub), exist_ok=True)
    return folder

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════
W, H = 1080, 1920

def lc(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def grad_bg(draw, top, bot):
    for y in range(H):
        draw.line([(0, y), (W, y)], fill=lc(top, bot, y/H))

def get_font(size=36):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]:
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()

# ═══════════════════════════════════════════════════════════════════════════
# 🤖 SUPERVISOR AGENT
# ═══════════════════════════════════════════════════════════════════════════
def run_supervisor(topic, user_story, num_scenes, phase_list):
    """
    Supervisor Agent:
    - If user gave their own story → enhance it, never replace
    - If just a topic → create full viral content
    - Optimizes hashtags, keywords, thumbnails
    - Returns complete structured package
    """
    has_user_story = len(user_story.strip()) > 30

    if has_user_story:
        instruction = f"""The user has provided THEIR OWN STORY below. Your job is to ENHANCE it — keep the core meaning, make it more dramatic, more emotional, more viral. DO NOT replace their story with something different.

USER'S STORY:
{user_story}

Now enhance this story into a {num_scenes}-scene suspense medical video script."""
    else:
        instruction = f"""Create a VIRAL SUSPENSE medical story from scratch for this topic: {topic}
Make it shocking, emotional, and impossible to stop watching."""

    phases_str = "\n".join([f"Scene {i+1}: {p.upper()}" for i, p in enumerate(phase_list)])

    prompt = f"""You are a SUPERVISOR AGENT for a world-class medical video factory.

{instruction}

STORY STRUCTURE:
{phases_str}

Phase rules:
- HOOK: Shocking opening. Viewer freezes.
- MYSTERY: Something wrong, answer hidden. Build dread.
- CLUE: One clue dropped. Curiosity grows.
- RISING: Tension peak. Viewer suspects truth.
- REVEAL: BIG DRAMATIC TRUTH revealed.
- RESOLUTION: Doctor advice + CTA for clinic.

OUTPUT FORMAT — write exactly in this order:

[SUPERVISOR_NOTES]
Write 2-3 lines about what makes this content viral and your quality decisions.

[HOOK_LINE]
One 5-7 word shocking Hindi opening line.

[CAPTION]
3-4 emotional Hindi lines for Instagram/YouTube caption. End with clinic CTA.

[HASHTAGS]
Exactly 25 hashtags — mix of Hindi medical, English medical, and trending. One line, space-separated.

[KEYWORDS]
10 SEO keywords for YouTube. Comma-separated.

[THUMBNAIL_TEXTS]
3 separate thumbnail text options (4-5 bold Hindi words each). Numbered 1-2-3.

[SCENES]
Write exactly {num_scenes} scene lines. STRICT FORMAT:
SCENE [N] | [PHASE] | [English medical keyword 3-5 words] | [Hindi dialogue 1-2 sentences]

[END]"""

    res = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        max_tokens=4500
    )
    return res.choices[0].message.content


def parse_supervisor_output(raw):
    """Extract all sections from supervisor output."""
    result = {}

    sections = ["SUPERVISOR_NOTES", "HOOK_LINE", "CAPTION", "HASHTAGS",
                "KEYWORDS", "THUMBNAIL_TEXTS", "SCENES"]

    for i, sec in enumerate(sections):
        pattern = r'\[' + sec + r'\](.*?)(?=\[' + (sections[i+1] if i+1 < len(sections) else 'END') + r'\]|\[END\]|$)'
        m = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        result[sec] = m.group(1).strip() if m else ""

    return result


# ═══════════════════════════════════════════════════════════════════════════
# BULLETPROOF SCENE PARSER
# ═══════════════════════════════════════════════════════════════════════════
VALID_PHASES = {"hook","mystery","clue","rising","reveal","resolution"}

def parse_scenes(raw_text, fallback_phases):
    scenes = []

    # FORMAT A: SCENE N | PHASE | keyword | hindi  (most common)
    matches = re.findall(
        r'SCENE\s*\d*\s*\|\s*([A-Za-z]+)\s*\|\s*([^|\n]+?)\s*\|\s*([^\n]+)',
        raw_text, re.IGNORECASE
    )
    if matches:
        for m in matches:
            phase = m[0].strip().lower()
            keyword = m[1].strip()
            hindi = m[2].strip()
            if keyword and hindi:
                if phase not in VALID_PHASES: phase = "clue"
                scenes.append({"phase": phase, "keyword": keyword, "hindi": hindi})
        if scenes: return scenes

    # FORMAT B: SCENE | keyword | hindi (no phase)
    matches = re.findall(
        r'SCENE\s*\d*\s*\|\s*([^|\n]+?)\s*\|\s*([^\n]+)',
        raw_text, re.IGNORECASE
    )
    if matches:
        for i, m in enumerate(matches):
            keyword = m[0].strip(); hindi = m[1].strip()
            phase = fallback_phases[i] if i < len(fallback_phases) else "clue"
            if keyword and hindi:
                scenes.append({"phase": phase, "keyword": keyword, "hindi": hindi})
        if scenes: return scenes

    # FORMAT C: Numbered lines
    matches = re.findall(
        r'^\s*\d+[\.\)]\s*([^\-—\n]{3,40})\s*[\-—]\s*([^\n]{10,})',
        raw_text, re.MULTILINE
    )
    if matches:
        for i, m in enumerate(matches):
            keyword = m[0].strip(); hindi = m[1].strip()
            phase = fallback_phases[i] if i < len(fallback_phases) else "clue"
            if keyword and hindi:
                scenes.append({"phase": phase, "keyword": keyword, "hindi": hindi})
        if scenes: return scenes

    # FORMAT D: Any pipe-separated line
    lines = [l.strip() for l in raw_text.split("\n") if "|" in l and len(l) > 20]
    for i, line in enumerate(lines[:12]):
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3:
            phase = fallback_phases[i] if i < len(fallback_phases) else "clue"
            keyword = parts[-2]; hindi = parts[-1]
            if keyword and hindi and len(hindi) > 5:
                scenes.append({"phase": phase, "keyword": keyword, "hindi": hindi})

    return scenes


def build_phase_list(n):
    if n <= 4:   return ["hook","clue","reveal","resolution"][:n]
    elif n == 5: return ["hook","mystery","clue","reveal","resolution"]
    elif n == 6: return ["hook","mystery","clue","clue","reveal","resolution"]
    elif n == 7: return ["hook","mystery","clue","rising","clue","reveal","resolution"]
    elif n == 8: return ["hook","mystery","clue","rising","clue","rising","reveal","resolution"]
    elif n == 9: return ["hook","mystery","clue","rising","clue","rising","clue","reveal","resolution"]
    else:
        base = ["hook","mystery","clue","rising","clue","rising","clue","rising","reveal","reveal","resolution","resolution"]
        return (base + ["clue","rising"]*6)[:n]


# ═══════════════════════════════════════════════════════════════════════════
# MOOD PALETTES
# ═══════════════════════════════════════════════════════════════════════════
MOODS = {
    "hook":       {"top":(30,0,0),   "bot":(8,0,0),   "ac":(255,60,60),  "tx":(255,200,200)},
    "mystery":    {"top":(10,0,35),  "bot":(2,0,10),  "ac":(140,80,255), "tx":(210,180,255)},
    "clue":       {"top":(0,20,45),  "bot":(0,5,15),  "ac":(40,160,255), "tx":(180,220,255)},
    "rising":     {"top":(30,15,0),  "bot":(10,5,0),  "ac":(255,160,0),  "tx":(255,230,170)},
    "reveal":     {"top":(0,35,15),  "bot":(0,10,5),  "ac":(0,220,120),  "tx":(180,255,210)},
    "resolution": {"top":(20,18,0),  "bot":(6,5,0),   "ac":(255,215,0),  "tx":(255,240,180)},
}
PHASE_EMOJI  = {"hook":"🔴","mystery":"🟣","clue":"🔵","rising":"🟠","reveal":"🟢","resolution":"🏆"}
PHASE_LABELS = {"hook":"HOOK — DANGER","mystery":"MYSTERY — SUSPENSE","clue":"CLUE — EVIDENCE",
                "rising":"RISING — TENSION","reveal":"REVEAL — THE TRUTH","resolution":"RESOLUTION — SOLUTION"}
PHASE_BAR    = {"hook":(70,0,0),"mystery":(25,0,70),"clue":(0,25,70),
                "rising":(70,35,0),"reveal":(0,55,25),"resolution":(55,45,0)}

# ═══════════════════════════════════════════════════════════════════════════
# 16 CARTOON SCENE DRAWERS
# ═══════════════════════════════════════════════════════════════════════════

def draw_heart(draw, ac, tx):
    cx, cy = W//2, H//2-100
    for g in range(8,0,-1):
        r=260+g*24; draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=tuple(max(0,c//6) for c in ac))
    draw.ellipse([cx-240,cy-200,cx+60,cy+80],fill=ac)
    draw.ellipse([cx-60,cy-200,cx+240,cy+80],fill=ac)
    draw.polygon([(cx-240,cy+40),(cx+240,cy+40),(cx,cy+260)],fill=ac)
    draw.ellipse([cx-130,cy-160,cx-50,cy-90],fill=tx)
    py=cy+380; pts=[]
    for x in range(60,W-60,10):
        t=(x-60)/(W-120)
        if 0.38<t<0.48: oy=-int(math.sin((t-0.38)*math.pi/0.1)*200)
        elif 0.48<t<0.55: oy=int(math.sin((t-0.48)*math.pi/0.1)*70)
        else: oy=0
        pts.append((x,py+oy))
    for i in range(len(pts)-1): draw.line([pts[i],pts[i+1]],fill=tx,width=8)

def draw_brain(draw, ac, tx):
    cx,cy=W//2,H//2-80
    draw.ellipse([cx-260,cy-220,cx+20,cy+210],fill=ac)
    draw.ellipse([cx-20,cy-220,cx+260,cy+210],fill=tuple(max(0,c-40) for c in ac))
    for i in range(7):
        ang=math.pi*i/7; x1=cx+int(190*math.cos(ang))-25; y1=cy+int(170*math.sin(ang))-25
        draw.arc([x1,y1,x1+50,y1+50],0,200,fill=tx,width=7)
    nodes=[(cx-180,cy-80),(cx-60,cy-150),(cx+90,cy-100),(cx+190,cy+50),(cx-100,cy+130),(cx+50,cy+170)]
    for i,n in enumerate(nodes):
        draw.ellipse([n[0]-16,n[1]-16,n[0]+16,n[1]+16],fill=tx)
        draw.line([n,nodes[(i+2)%len(nodes)]],fill=tx,width=4)

def draw_lungs(draw, ac, tx):
    cx,cy=W//2,H//2-40
    draw.ellipse([cx-290,cy-210,cx-20,cy+250],fill=ac)
    draw.ellipse([cx+20,cy-210,cx+290,cy+250],fill=tuple(max(0,c-30) for c in ac))
    draw.rectangle([cx-20,cy-330,cx+20,cy-190],fill=tx)
    draw.line([(cx,cy-190),(cx-140,cy-70)],fill=tx,width=14)
    draw.line([(cx,cy-190),(cx+140,cy-70)],fill=tx,width=14)
    for s in [-1,1]:
        bx=cx+s*140
        for b in range(4):
            by=cy-70+b*55; draw.line([(bx+s*b*20,by),(bx+s*(b*20+50),by+45)],fill=tx,width=7)

def draw_dna(draw, ac, tx):
    cx=W//2
    for y in range(200,H-200,18):
        t=(y-200)/(H-400); ang=t*math.pi*5
        x1=cx+int(200*math.cos(ang)); x2=cx+int(200*math.cos(ang+math.pi))
        draw.ellipse([x1-18,y-18,x1+18,y+18],fill=lc(ac,tx,abs(math.sin(ang))))
        draw.ellipse([x2-18,y-18,x2+18,y+18],fill=lc(ac,tx,abs(math.cos(ang))))
        if y%54<18: draw.line([(x1,y),(x2,y)],fill=tx,width=5)

def draw_blood_cells(draw, ac, tx):
    import random; random.seed(42)
    for i in range(30):
        x=random.randint(80,W-80); y=random.randint(300,H-300); r=random.randint(28,55)
        col=ac if i%4!=0 else (240,240,255)
        draw.ellipse([x-r,y-r,x+r,y+r],fill=col)
        draw.ellipse([x-r//2,y-r//2,x+r//2,y+r//2],fill=tuple(max(0,c-60) for c in col))
    for fy in range(400,H-300,120):
        for fx in range(60,W-60,180):
            draw.polygon([(fx,fy),(fx+30,fy-20),(fx+30,fy+20)],fill=tx)

def draw_pill(draw, ac, tx):
    cx,cy=W//2,H//2-60
    draw.ellipse([cx-180,cy-80,cx+20,cy+80],fill=ac)
    draw.ellipse([cx-20,cy-80,cx+180,cy+80],fill=tx)
    draw.rectangle([cx-20,cy-80,cx+20,cy+80],fill=(200,200,220))
    for i in range(6):
        ang=2*math.pi*i/6; mx=cx+int(310*math.cos(ang)); my=cy+int(310*math.sin(ang))
        draw.ellipse([mx-22,my-22,mx+22,my+22],fill=ac)
        draw.line([(mx,my),(cx+int(160*math.cos(ang)),cy+int(160*math.sin(ang)))],fill=tx,width=5)

def draw_surgery(draw, ac, tx):
    cx,cy=W//2,H//2
    draw.rounded_rectangle([cx-320,cy-30,cx+320,cy+50],radius=20,fill=(60,60,80))
    draw.rounded_rectangle([cx-280,cy-80,cx+280,cy-30],radius=10,fill=(80,80,100))
    draw.ellipse([cx-55,cy-160,cx+55,cy-60],fill=(220,180,140))
    draw.rounded_rectangle([cx-80,cy-60,cx+80,cy-30],radius=8,fill=(220,180,140))
    draw.polygon([(cx,cy-500),(cx-160,cy-120),(cx+160,cy-120)],fill=(255,255,200))
    draw.ellipse([cx-30,cy-530,cx+30,cy-470],fill=ac)
    for ox,oy in [(cx-220,cy+100),(cx+220,cy+100),(cx-180,cy+140),(cx+180,cy+140)]:
        draw.rectangle([ox-8,oy-50,ox+8,oy+50],fill=tx)
        draw.ellipse([ox-12,oy-60,ox+12,oy-40],fill=ac)

def draw_skeleton(draw, ac, tx):
    cx,cy=W//2,H//2-40
    draw.ellipse([cx-90,cy-300,cx+90,cy-140],fill=ac)
    draw.ellipse([cx-50,cy-170,cx+50,cy-140],fill=(5,5,15))
    draw.rectangle([cx-25,cy-140,cx+25,cy-110],fill=ac)
    for i in range(8):
        sy=cy-100+i*55; draw.rounded_rectangle([cx-28,sy,cx+28,sy+40],radius=8,fill=ac)
    for side in [-1,1]:
        for i in range(5):
            ry=cy-60+i*45
            draw.polygon([(cx+side*28,ry),(cx+side*160,ry-15),(cx+side*170,ry+20),(cx+side*28,ry+28)],fill=ac)
    draw.line([(cx-28,cy-80),(cx-200,cy+60),(cx-180,cy+220)],fill=ac,width=22)
    draw.line([(cx+28,cy-80),(cx+200,cy+60),(cx+180,cy+220)],fill=ac,width=22)

def draw_virus(draw, ac, tx):
    import random; random.seed(7)
    cx,cy=W//2,H//2
    draw.ellipse([cx-140,cy-140,cx+140,cy+140],fill=(60,120,60))
    draw.ellipse([cx-60,cy-60,cx+60,cy+60],fill=(80,160,80))
    for i in range(12):
        vx=random.randint(60,W-60); vy=random.randint(200,H-200)
        if abs(vx-cx)<200 and abs(vy-cy)<200: vx+=220
        r=random.randint(30,55)
        draw.ellipse([vx-r,vy-r,vx+r,vy+r],fill=ac)
        for sp in range(8):
            sa=2*math.pi*sp/8
            draw.line([(vx+int(r*math.cos(sa)),vy+int(r*math.sin(sa))),(vx+int((r+22)*math.cos(sa)),vy+int((r+22)*math.sin(sa)))],fill=ac,width=5)

def draw_hospital(draw, ac, tx):
    cx,cy=W//2,H//2
    draw.rectangle([0,H//2,W,H],fill=(25,25,35)); draw.rectangle([0,0,W,H//2],fill=(18,18,28))
    draw.rounded_rectangle([80,cy-60,W-80,cy+180],radius=18,fill=(70,70,90))
    draw.rounded_rectangle([100,cy-100,W-100,cy-60],radius=12,fill=(200,180,160))
    draw.rounded_rectangle([W-340,cy-320,W-60,cy-140],radius=14,fill=(20,20,30))
    draw.rectangle([W-320,cy-300,W-80,cy-160],fill=(0,20,0))
    pts=[]; py=cy-230
    for x in range(W-310,W-90,8):
        t=(x-(W-310))/220; oy=-int(math.sin((t-0.4)*math.pi/0.12)*60) if 0.4<t<0.52 else 0
        pts.append((x,py+oy))
    for i in range(len(pts)-1): draw.line([pts[i],pts[i+1]],fill=(0,255,0),width=4)
    draw.ellipse([W-520,cy-400,W-440,cy-320],fill=tx)
    draw.line([(W-480,cy-320),(W-480,cy-60)],fill=tx,width=5)

def draw_warning(draw, ac, tx):
    cx,cy=W//2,H//2
    draw.polygon([(cx,cy-340),(cx-300,cy+160),(cx+300,cy+160)],fill=ac)
    draw.polygon([(cx,cy-270),(cx-240,cy+120),(cx+240,cy+120)],fill=(8,8,20))
    draw.rectangle([cx-22,cy-180,cx+22,cy+30],fill=ac)
    draw.ellipse([cx-24,cy+55,cx+24,cy+105],fill=ac)
    for ex,ey in [(140,340),(W-140,340),(140,H-340),(W-140,H-340)]:
        draw.rectangle([ex-10,ey-50,ex+10,ey+20],fill=ac)
        draw.ellipse([ex-12,ey+35,ex+12,ey+65],fill=ac)

def draw_microscope(draw, ac, tx):
    cx,cy=W//2,H//2
    draw.rectangle([cx-25,cy-320,cx+25,cy+40],fill=ac)
    draw.rectangle([cx-80,cy-360,cx+80,cy-300],fill=ac)
    draw.ellipse([cx-40,cy-380,cx+40,cy-300],fill=tx)
    draw.line([(cx,cy+40),(cx-130,cy+200),(cx+130,cy+200)],fill=ac,width=30)
    draw.ellipse([cx-220,cy-260,cx+220,cy+180],fill=(10,30,10))
    for bx,by,br in [(cx-60,cy-80,38),(cx+70,cy-40,30),(cx-30,cy+80,45),(cx+100,cy+90,28)]:
        draw.ellipse([bx-br,by-br,bx+br,by+br],fill=(50,200,80))
        draw.ellipse([bx-br//2,by-br//2,bx+br//2,by+br//2],fill=(30,150,50))

def draw_xray(draw, ac, tx):
    cx,cy=W//2,H//2-60
    draw.rectangle([cx-280,cy-360,cx+280,cy+360],fill=(8,8,20))
    for i in range(6):
        ry=cy-200+i*70
        for s in [-1,1]:
            draw.polygon([(cx+s*30,ry),(cx+s*220,ry-20),(cx+s*230,ry+35),(cx+s*30,ry+50)],fill=ac)
    for i in range(12):
        sy=cy-220+i*45; draw.rounded_rectangle([cx-18,sy,cx+18,sy+32],radius=6,fill=tx)
    draw.ellipse([cx-80,cy-150,cx+10,cy-50],fill=(200,50,50))
    draw.ellipse([cx-10,cy-150,cx+80,cy-50],fill=(180,40,40))

def draw_injection(draw, ac, tx):
    cx,cy=W//2,H//2
    draw.polygon([(cx-200,cy-40),(cx+180,cy-40),(cx+200,cy),(cx+180,cy+40),(cx-200,cy+40)],fill=(200,200,220))
    draw.rectangle([cx-200,cy-20,cx-160,cy+20],fill=(160,160,180))
    draw.polygon([(cx+200,cy-8),(cx+330,cy),(cx+200,cy+8)],fill=tx)
    draw.rectangle([cx-190,cy-28,cx-40,cy+28],fill=ac)
    draw.rectangle([cx-220,cy-40,cx-200,cy+40],fill=ac)
    for i in range(5):
        ang=2*math.pi*i/5; mx=cx+int(260*math.cos(ang)); my=cy+int(260*math.sin(ang))
        draw.ellipse([mx-18,my-18,mx+18,my+18],fill=ac)

def draw_detective(draw, ac, tx):
    cx,cy=W//2,H//2-60; dim=tuple(c//4 for c in ac)
    for qx,qy in [(160,300),(W-160,300),(200,H-350),(W-200,H-350),(cx,220)]:
        draw.arc([qx-35,qy-50,qx+35,qy+20],200,400,fill=dim,width=8)
        draw.ellipse([qx-6,qy+30,qx+6,qy+46],fill=dim)
    draw.ellipse([cx-200,cy-200,cx+200,cy+200],fill=(20,25,40))
    draw.ellipse([cx-180,cy-180,cx+180,cy+180],fill=(10,15,25))
    draw.ellipse([cx-80,cy-80,cx+10,cy+10],fill=(220,50,50))
    draw.ellipse([cx-10,cy-80,cx+80,cy+10],fill=(200,40,40))
    draw.polygon([(cx-80,cy-20),(cx+80,cy-20),(cx,cy+80)],fill=(210,45,45))
    draw.line([(cx+190,cy+190),(cx+340,cy+340)],fill=tx,width=30)
    draw.ellipse([cx+310,cy+310,cx+370,cy+370],fill=ac)

def draw_reveal_burst(draw, ac, tx):
    cx,cy=W//2,H//2-80
    for i in range(24):
        ang=2*math.pi*i/24
        x1=cx+int(80*math.cos(ang)); y1=cy+int(80*math.sin(ang))
        x2=cx+int(460*math.cos(ang)); y2=cy+int(460*math.sin(ang))
        draw.line([(x1,y1),(x2,y2)],fill=tuple(min(255,c+50) for c in ac),width=8 if i%2==0 else 4)
    for r in [220,180,140,100,60]:
        draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=lc(ac,tx,1-r/220))
    draw.line([(cx-60,cy),(cx-10,cy+60),(cx+80,cy-60)],fill=(255,255,255),width=18)

SCENE_DRAWERS = {
    "heart":draw_heart,"brain":draw_brain,"lungs":draw_lungs,"dna":draw_dna,
    "blood_cells":draw_blood_cells,"pill":draw_pill,"surgery":draw_surgery,
    "skeleton":draw_skeleton,"virus":draw_virus,"hospital":draw_hospital,
    "warning":draw_warning,"microscope":draw_microscope,"xray":draw_xray,
    "injection":draw_injection,"detective":draw_detective,"reveal_burst":draw_reveal_burst,
}
CYCLE_ORDER = list(SCENE_DRAWERS.keys())

def pick_scene(keyword, phase, idx):
    kw=keyword.lower()
    if any(w in kw for w in ["heart","cardiac","attack","chest","coronary","artery","myocard","infarct","fail"]): return "heart"
    if any(w in kw for w in ["brain","stroke","neuro","memory","headache","alzheimer"]): return "brain"
    if any(w in kw for w in ["lung","breath","asthma","oxygen","respiratory"]): return "lungs"
    if any(w in kw for w in ["dna","gene","cancer","tumor","chromosome"]): return "dna"
    if any(w in kw for w in ["blood","cell","hemoglobin","anemia","clot","pressure","bp"]): return "blood_cells"
    if any(w in kw for w in ["medicine","pill","drug","tablet","treatment","dose"]): return "pill"
    if any(w in kw for w in ["surgery","operation","bypass","transplant"]): return "surgery"
    if any(w in kw for w in ["bone","joint","fracture","calcium","osteo"]): return "skeleton"
    if any(w in kw for w in ["virus","bacteria","infection","fever","immune","covid"]): return "virus"
    if any(w in kw for w in ["hospital","ward","icu","patient","echo","cardiology"]): return "hospital"
    if any(w in kw for w in ["warning","sign","symptom","danger","risk","silent"]): return "warning"
    if any(w in kw for w in ["test","lab","biopsy","pathology","diagnosis"]): return "microscope"
    if any(w in kw for w in ["xray","scan","mri","ct","imaging"]): return "xray"
    if any(w in kw for w in ["inject","vaccine","insulin","iv","syringe"]): return "injection"
    phase_map={"hook":"warning","mystery":"detective","clue":"microscope","rising":"xray","reveal":"reveal_burst","resolution":"hospital"}
    return phase_map.get(phase, CYCLE_ORDER[idx % len(CYCLE_ORDER)])


# ═══════════════════════════════════════════════════════════════════════════
# 👨‍⚕️ CARTOON DOCTOR MASCOT — "Dr. Aarav"
# ═══════════════════════════════════════════════════════════════════════════
def draw_doctor_mascot(draw, text_hint="", ac=(255,215,0)):
    """
    Cartoon Doctor Human — bottom-right corner.
    White coat, stethoscope, pointing finger downward.
    Speech bubble with short hint text.
    """
    # Position: bottom-right
    bx = W - 260   # base x (center of doctor)
    by = H - 320   # base y (feet level)

    # ── BODY (white coat) ──────────────────────────────────
    # Legs
    draw.rounded_rectangle([bx-28,by-120,bx-8,by],  radius=10, fill=(100,120,180))
    draw.rounded_rectangle([bx+8, by-120,bx+28,by],  radius=10, fill=(100,120,180))
    # Shoes
    draw.rounded_rectangle([bx-38,by-18,bx,by+10],   radius=8,  fill=(40,40,60))
    draw.rounded_rectangle([bx,   by-18,bx+38,by+10],radius=8,  fill=(40,40,60))
    # White coat body
    draw.rounded_rectangle([bx-55,by-290,bx+55,by-110],radius=18,fill=(240,240,255))
    # Coat lapels
    draw.polygon([(bx-55,by-290),(bx-15,by-290),(bx-15,by-200),(bx-55,by-240)],fill=(220,220,240))
    draw.polygon([(bx+55,by-290),(bx+15,by-290),(bx+15,by-200),(bx+55,by-240)],fill=(220,220,240))
    # Red cross on coat
    draw.rectangle([bx-8,by-270,bx+8,by-230], fill=(220,40,40))
    draw.rectangle([bx-20,by-258,bx+20,by-242],fill=(220,40,40))
    # Stethoscope
    draw.arc([bx-30,by-230,bx+30,by-170], 180, 0, fill=(60,60,80), width=8)
    draw.ellipse([bx-18,by-174,bx+2,by-158],fill=(60,60,80))
    draw.ellipse([bx+12,by-186,bx+28,by-170],fill=(180,180,200))

    # ── HEAD ───────────────────────────────────────────────
    # Neck
    draw.rounded_rectangle([bx-14,by-320,bx+14,by-292],radius=6,fill=(255,210,170))
    # Head
    draw.ellipse([bx-52,by-420,bx+52,by-310],fill=(255,210,170))
    # Hair
    draw.ellipse([bx-52,by-420,bx+52,by-365],fill=(60,40,20))
    draw.ellipse([bx-45,by-410,bx+45,by-370],fill=(80,55,25))
    # Eyes
    draw.ellipse([bx-28,by-390,bx-10,by-372],fill=(255,255,255))
    draw.ellipse([bx+10,by-390,bx+28,by-372],fill=(255,255,255))
    draw.ellipse([bx-24,by-386,bx-14,by-376],fill=(40,80,160))
    draw.ellipse([bx+14,by-386,bx+24,by-376],fill=(40,80,160))
    draw.ellipse([bx-21,by-383,bx-17,by-379],fill=(0,0,0))
    draw.ellipse([bx+17,by-383,bx+21,by-379],fill=(0,0,0))
    # Eyebrows
    draw.arc([bx-30,by-400,bx-8,by-380],200,340,fill=(60,40,20),width=5)
    draw.arc([bx+8, by-400,bx+30,by-380],200,340,fill=(60,40,20),width=5)
    # Smile
    draw.arc([bx-20,by-368,bx+20,by-348],10,170,fill=(180,80,80),width=5)
    # Ears
    draw.ellipse([bx-62,by-388,bx-44,by-366],fill=(255,190,150))
    draw.ellipse([bx+44,by-388,bx+62,by-366],fill=(255,190,150))
    # Doctor cap
    draw.rounded_rectangle([bx-48,by-428,bx+48,by-412],radius=6,fill=(255,255,255))
    draw.rectangle([bx-6,by-445,bx+6,by-428],fill=(255,255,255))
    draw.rectangle([bx-16,by-448,bx+16,by-440],fill=(255,255,255))

    # ── ARMS ───────────────────────────────────────────────
    # Left arm (normal)
    draw.rounded_rectangle([bx-80,by-280,bx-55,by-160],radius=12,fill=(240,240,255))
    draw.ellipse([bx-88,by-175,bx-50,by-145],fill=(255,210,170))
    # Right arm (pointing DOWN with finger)
    draw.rounded_rectangle([bx+55,by-280,bx+80,by-160],radius=12,fill=(240,240,255))
    # Hand pointing down
    draw.ellipse([bx+48,by-155,bx+86,by-125],fill=(255,210,170))
    # Pointing finger (downward)
    draw.rounded_rectangle([bx+60,by-125,bx+74,by-75],radius=8,fill=(255,210,170))
    # Arrow indicating downward
    draw.polygon([(bx+67,by-60),(bx+50,by-88),(bx+84,by-88)],fill=ac)

    # ── SPEECH BUBBLE (short hint) ─────────────────────────
    if text_hint:
        bubble_x = bx - 280
        bubble_y = by - 440
        bubble_w = 240
        bubble_h = 70
        # Bubble background
        draw.rounded_rectangle([bubble_x,bubble_y,bubble_x+bubble_w,bubble_y+bubble_h],
                                radius=18,fill=(255,255,255))
        draw.rounded_rectangle([bubble_x+2,bubble_y+2,bubble_x+bubble_w-2,bubble_y+bubble_h-2],
                                radius=16,fill=(255,252,230))
        # Bubble tail pointing right toward doctor
        draw.polygon([(bubble_x+bubble_w,bubble_y+bubble_h-20),
                      (bubble_x+bubble_w+30,bubble_y+bubble_h-10),
                      (bubble_x+bubble_w,bubble_y+bubble_h-40)],fill=(255,252,230))
        draw.polygon([(bubble_x+bubble_w,bubble_y+bubble_h-20),
                      (bubble_x+bubble_w+30,bubble_y+bubble_h-10),
                      (bubble_x+bubble_w,bubble_y+bubble_h-40)],outline=(200,180,100),width=2)
        # Text inside bubble
        hint = text_hint[:22]
        f_hint = get_font(24)
        try:
            bb = draw.textbbox((0,0), hint, font=f_hint)
            tw = bb[2]-bb[0]
        except: tw = len(hint)*13
        tx_pos = bubble_x + (bubble_w - tw)//2
        draw.text((tx_pos, bubble_y+18), hint, fill=(40,40,80), font=f_hint)


# ═══════════════════════════════════════════════════════════════════════════
# 🏥 BRANDING PLATE — Bottom Left
# ═══════════════════════════════════════════════════════════════════════════
def draw_branding_plate(draw, clinic_name, doctor_name, addr1, addr2, addr3, phone):
    """Draw clinic branding plate — bottom left corner."""
    px, py = 30, H - 380
    pw, ph = 380, 340

    # Plate background
    draw.rounded_rectangle([px, py, px+pw, py+ph], radius=16, fill=(0,0,0))
    draw.rounded_rectangle([px+2, py+2, px+pw-2, py+ph-2], radius=14, fill=(8,8,20))
    # Gold border
    for i in range(3):
        draw.rounded_rectangle([px+i, py+i, px+pw-i, py+ph-i],
                                radius=16-i, outline=(255,215,0), width=1)

    # Red cross icon
    draw.rectangle([px+18, py+15, px+28, py+50], fill=(220,40,40))
    draw.rectangle([px+10, py+24, px+36, py+40], fill=(220,40,40))

    # Clinic name (gold, large)
    f_clinic = get_font(32)
    f_small  = get_font(24)
    f_tiny   = get_font(20)

    draw.text((px+46, py+14), clinic_name[:22], fill=(255,215,0), font=f_clinic)
    # Underline
    draw.line([(px+10, py+58), (px+pw-10, py+58)], fill=(255,215,0), width=2)

    # Doctor name
    draw.text((px+14, py+68), doctor_name[:28], fill=(200,220,255), font=f_small)

    # Address lines
    y_off = py + 104
    for line in [addr1, addr2, addr3]:
        if line.strip():
            draw.text((px+14, y_off), line[:32], fill=(180,180,200), font=f_tiny)
            y_off += 30

    # Phone
    if phone.strip():
        draw.text((px+14, y_off+6), "📞 " + phone[:20], fill=(255,215,0), font=f_tiny)

    # Bottom accent bar
    draw.rounded_rectangle([px+10, py+ph-28, px+pw-10, py+ph-10],
                            radius=8, fill=(255,215,0))
    draw.text((px+14, py+ph-26), "Expert Care · Trusted Results", fill=(0,0,0), font=f_tiny)


# ═══════════════════════════════════════════════════════════════════════════
# THUMBNAIL GENERATOR
# ═══════════════════════════════════════════════════════════════════════════
def create_thumbnail(title_text, subtitle, ac, folder):
    """Generate eye-catching thumbnail 1280x720."""
    TW, TH = 1280, 720
    img = Image.new("RGB", (TW, TH))
    draw = ImageDraw.Draw(img)

    # Dramatic gradient
    for y in range(TH):
        t = y/TH
        c = lc((20,0,0), (0,0,20), t)
        draw.line([(0,y),(TW,y)], fill=c)

    # Diagonal accent
    draw.polygon([(0,0),(TW//2,0),(0,TH//2)], fill=tuple(max(0,c//4) for c in ac))

    # Central glow
    for r in range(300,0,-20):
        alpha_c = tuple(int(c * (1 - r/300) * 0.3) for c in ac)
        draw.ellipse([TW//2-r,TH//2-r,TW//2+r,TH//2+r], fill=alpha_c)

    # Title text
    f_title = get_font(80)
    f_sub   = get_font(44)
    words   = title_text[:40].upper()
    try:
        bb = draw.textbbox((0,0), words, font=f_title)
        tw = bb[2]-bb[0]
    except: tw = len(words)*44
    # Shadow
    draw.text(((TW-tw)//2+4, TH//2-90+4), words, fill=(0,0,0), font=f_title)
    draw.text(((TW-tw)//2,   TH//2-90),   words, fill=ac,       font=f_title)

    # Subtitle
    sub = subtitle[:50]
    try:
        bb2 = draw.textbbox((0,0), sub, font=f_sub)
        tw2 = bb2[2]-bb2[0]
    except: tw2 = len(sub)*24
    draw.text(((TW-tw2)//2, TH//2+20), sub, fill=(255,255,255), font=f_sub)

    # Bottom bar
    draw.rectangle([0,TH-70,TW,TH], fill=(0,0,0))
    draw.text((20, TH-56), "DR. VASU MEMORIAL CLINIC · MODINAGAR", fill=(255,215,0), font=get_font(32))

    path = os.path.join(folder, "thumbnails", f"thumb_{int(time.time())}.png")
    img.save(path)
    return path


# ═══════════════════════════════════════════════════════════════════════════
# MAIN FRAME BUILDER
# ═══════════════════════════════════════════════════════════════════════════
def build_frame(keyword, phase, idx, total, folder,
                clinic_name, doctor_name, addr1, addr2, addr3, phone):
    mood  = MOODS.get(phase, MOODS["clue"])
    stype = pick_scene(keyword, phase, idx)
    fn    = SCENE_DRAWERS.get(stype, draw_warning)

    img  = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # Background + scene cartoon
    grad_bg(draw, mood["top"], mood["bot"])
    fn(draw, mood["ac"], mood["tx"])

    # Top phase bar
    draw.rectangle([0,0,W,112], fill=PHASE_BAR.get(phase,(20,20,50)))
    label = PHASE_LABELS.get(phase, phase.upper())
    f = get_font(38)
    try:
        bb = draw.textbbox((0,0), label, font=f); tw = bb[2]-bb[0]
    except: tw = len(label)*20
    draw.text(((W-tw)//2, 33), label, fill=mood["ac"], font=f)

    # Bottom keyword bar
    draw.rectangle([0,H-130,W,H], fill=tuple(max(0,c//5) for c in mood["ac"]))
    kw_disp = keyword.upper()[:32]
    f2 = get_font(32)
    try:
        bb2 = draw.textbbox((0,0), kw_disp, font=f2); tw2 = bb2[2]-bb2[0]
    except: tw2 = len(kw_disp)*17
    draw.text(((W-tw2)//2, H-105), kw_disp, fill=mood["tx"], font=f2)

    # Progress dots
    for d in range(total):
        dx = W//2-(total*28)//2+d*28+14
        draw.ellipse([dx-9,H-48-9,dx+9,H-48+9], fill=mood["ac"] if d==idx else (40,40,60))

    # Branding plate — bottom left
    draw_branding_plate(draw, clinic_name, doctor_name, addr1, addr2, addr3, phone)

    # Doctor mascot — bottom right
    short_hint = PHASE_LABELS.get(phase,"").split("—")[0].strip()[:18]
    draw_doctor_mascot(draw, short_hint, mood["ac"])

    # Vignette
    vig = Image.new("RGBA",(W,H),(0,0,0,0))
    vd  = ImageDraw.Draw(vig)
    for i in range(80):
        vd.rectangle([i,i,W-i,H-i],outline=(0,0,0,int(170*(i/80)**1.8)),width=1)
    out = Image.alpha_composite(img.convert("RGBA"),vig).convert("RGB")

    path = os.path.join(folder, "frames", f"s{idx}_{stype}.png")
    out.save(path)
    return path


# ═══════════════════════════════════════════════════════════════════════════
# VOICE
# ═══════════════════════════════════════════════════════════════════════════
async def tts(text, path):
    await edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+50%", pitch="-12Hz").save(path)

def get_dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",path],capture_output=True,text=True)
    try:    return max(float(r.stdout.strip()),2.0)
    except: return 3.5


# ═══════════════════════════════════════════════════════════════════════════
# VIDEO ENGINE
# ═══════════════════════════════════════════════════════════════════════════
def ken_burns(img, dur, idx, folder):
    out = os.path.join(folder,"clips",f"kb_{idx}.ts")
    frames = max(int(dur*25),55)
    pats = [
        ("min(zoom+0.0020,1.60)","iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)"),
        ("if(eq(on,1),1.50,max(zoom-0.0018,1.0))","iw/2-(iw/zoom/2)+on*0.28","ih/3-(ih/zoom/3)"),
        ("min(zoom+0.0014,1.38)","iw/3-(iw/zoom/3)+on*0.18","ih/2-(ih/zoom/2)"),
        ("if(eq(on,1),1.45,max(zoom-0.0012,1.0))","iw*2/3-(iw/zoom/2)","ih/2-(ih/zoom/2)"),
    ]
    z,x,y = pats[idx%4]
    cmd = (f'ffmpeg -y -loop 1 -i "{img}" '
           f'-vf "zoompan=z=\'{z}\':d={frames}:x=\'{x}\':y=\'{y}\':s=1080x1920:fps=25,scale=1080:1920" '
           f'-t {dur:.3f} -c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning')
    subprocess.run(cmd,shell=True)
    return out if(os.path.exists(out) and os.path.getsize(out)>500) else None

def burn_sub(clip, text, idx, folder):
    out  = os.path.join(folder,"clips",f"sub_{idx}.ts")
    safe = re.sub(r'[\"\':\\%<>]',' ',text)[:70]
    cmd  = (f'ffmpeg -y -i "{clip}" '
            f'-vf "drawtext=text=\'{safe}\':fontcolor=white:fontsize=42:'
            f'x=(w-text_w)/2:y=h-210:box=1:boxcolor=black@0.75:boxborderw=20" '
            f'-c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning')
    subprocess.run(cmd,shell=True)
    return out if(os.path.exists(out) and os.path.getsize(out)>500) else clip

def concat_ts(paths, out):
    lst = out.replace(".mp4",".txt")
    with open(lst,"w") as f:
        for p in paths: f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{out}" -loglevel warning',shell=True)

def concat_aud(paths, out):
    lst = out.replace(".mp3","_list.txt")
    with open(lst,"w") as f:
        for p in paths: f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(f'ffmpeg -y -f concat -safe 0 -i "{lst}" -c copy "{out}" -loglevel warning',shell=True)

def final_render(vid, aud, out):
    cmd = (f'ffmpeg -y -i "{vid}" -i "{aud}" '
           f'-filter_complex "'
           f'[0:v]vignette=PI/5[v1];'
           f'[v1]eq=contrast=1.12:brightness=0.03:saturation=1.2[v2];'
           f'[v2]drawbox=y=0:x=0:w=iw:h=112:color=black@0.9:t=fill[v3];'
           f'[v3]drawtext=text=\'DR. VASU MEMORIAL CLINIC\':'
           f'fontcolor=#FFD700:fontsize=42:x=(w-text_w)/2:y=33[vf]" '
           f'-map "[vf]" -map 1:a -c:v libx264 -preset fast '
           f'-c:a aac -b:a 192k -shortest -movflags +faststart "{out}" -loglevel warning')
    subprocess.run(cmd,shell=True)


# ═══════════════════════════════════════════════════════════════════════════
# ZIP PACKAGER
# ═══════════════════════════════════════════════════════════════════════════
def create_zip(folder, supervised, topic):
    """Create full ZIP package with all assets."""
    zip_path = folder + ".zip"

    # Save content files
    content_dir = os.path.join(folder,"content")
    with open(os.path.join(content_dir,"full_package.txt"),"w",encoding="utf-8") as f:
        f.write(f"Topic: {topic}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("="*50 + "\n")
        for key, val in supervised.items():
            f.write(f"\n[{key}]\n{val}\n")

    with open(os.path.join(content_dir,"hashtags.txt"),"w",encoding="utf-8") as f:
        f.write(supervised.get("HASHTAGS",""))

    with open(os.path.join(content_dir,"caption.txt"),"w",encoding="utf-8") as f:
        f.write(supervised.get("CAPTION",""))

    with open(os.path.join(content_dir,"keywords.txt"),"w",encoding="utf-8") as f:
        f.write(supervised.get("KEYWORDS",""))

    # Build ZIP
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder):
            for file in files:
                filepath = os.path.join(root, file)
                arcname  = os.path.relpath(filepath, os.path.dirname(folder))
                zf.write(filepath, arcname)

    return zip_path


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR — BRANDING + SETTINGS
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🏥 CLINIC BRANDING")
    st.caption("Fill once — applies to all videos automatically")

    st.session_state.clinic_name = st.text_input("Clinic Name:", value=st.session_state.clinic_name)
    st.session_state.doctor_name = st.text_input("Doctor Name:", value=st.session_state.doctor_name)
    st.session_state.address1    = st.text_input("Address Line 1:", value=st.session_state.address1)
    st.session_state.address2    = st.text_input("Address Line 2:", value=st.session_state.address2)
    st.session_state.address3    = st.text_input("City:", value=st.session_state.address3)
    st.session_state.phone       = st.text_input("Phone (optional):", value=st.session_state.phone)

    # Live brand preview
    st.markdown(f"""
    <div class="brand-preview">
    🏥 <b>{st.session_state.clinic_name}</b><br>
    👨‍⚕️ {st.session_state.doctor_name}<br>
    📍 {st.session_state.address1}<br>
    {st.session_state.address2}<br>
    {st.session_state.address3}<br>
    {"📞 " + st.session_state.phone if st.session_state.phone else ""}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ VIDEO SETTINGS")
    num_scenes = st.slider("📽️ Scenes:", 5, 12, 7)
    add_subs   = st.checkbox("📝 Hindi Subtitles", True)
    show_prev  = st.checkbox("🖼️ Show Frame Previews", True)

    st.markdown("---")
    st.markdown("### 🔬 IDEATION AGENT")
    broad = st.text_input("Topic for viral angles:", placeholder="e.g. Heart Failure")
    if st.button("🔍 5 VIRAL ANGLES"):
        if broad.strip():
            with st.spinner("Scanning trends..."):
                r = client.chat.completions.create(
                    messages=[{"role":"user","content":
                        f"Viral Hindi medical content strategist. Topic: {broad}. "
                        f"5 shocking suspense-style angles in Hindi (Devanagari). "
                        f"Each: 1 dramatic line. Numbered 1-5. Thriller style."}],
                    model="llama-3.3-70b-versatile",max_tokens=450)
                st.session_state.angles = r.choices[0].message.content
        else: st.warning("Enter a topic.")
    if st.session_state.angles: st.info(st.session_state.angles)

    st.markdown("---")
    st.markdown("### 🛠️ Live Production Log")
    logbox = st.empty()


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1 — CONTENT INPUT
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card"><span class="badge">STAGE 1 — SUPERVISOR AGENT</span>', unsafe_allow_html=True)

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
    placeholder="e.g. Heart Failure ke 3 khamoosh signs"
)

user_story = st.text_area(
    "✍️ Apni Story (Optional) — agar khud likhi hai toh yahan daalein:",
    placeholder="Agar aap khud ki story denge toh Agent isse enhance karega, replace nahi karega...\n\nKhaali chhod denge toh Agent khud viral content banayega.",
    height=120
)

if st.button("⚡ SUPERVISOR AGENT — GENERATE PACKAGE"):
    if not topic.strip():
        st.warning("Please enter a medical topic.")
    else:
        with st.status("🤖 Supervisor Agent working...", expanded=True) as status:
            phase_list = build_phase_list(num_scenes)

            if user_story.strip():
                st.write("📝 User story detected — Agent will ENHANCE your story, not replace it...")
            else:
                st.write("🎯 No story given — Agent creating full viral content from scratch...")

            st.write("Running Supervisor Agent quality check...")
            raw = run_supervisor(topic, user_story, num_scenes, phase_list)
            st.session_state.raw_llm = raw
            st.session_state.package = raw

            supervised = parse_supervisor_output(raw)
            st.session_state.supervised = supervised

            scenes = parse_scenes(supervised.get("SCENES","") or raw, phase_list)
            st.session_state.scenes = scenes
            n = len(scenes)

            status.update(label=f"✅ Supervisor Agent done! {n} scenes ready.", state="complete")

st.markdown("</div>", unsafe_allow_html=True)

# ── Show package ─────────────────────────────────────────────────────────
if st.session_state.supervised:
    sup = st.session_state.supervised

    # Agent notes
    if sup.get("SUPERVISOR_NOTES"):
        st.markdown(f"""
        <div class="agent-box">
        🤖 <b>Supervisor Agent Notes:</b><br>{sup["SUPERVISOR_NOTES"]}
        </div>""", unsafe_allow_html=True)

    # Content sections
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🎣 Hook Line"):
            st.write(sup.get("HOOK_LINE","—"))
        with st.expander("📝 Caption"):
            st.write(sup.get("CAPTION","—"))
        with st.expander("🖼️ Thumbnail Texts (3 options)"):
            st.write(sup.get("THUMBNAIL_TEXTS","—"))
    with col2:
        with st.expander("#️⃣ Hashtags (25)"):
            st.write(sup.get("HASHTAGS","—"))
        with st.expander("🔑 SEO Keywords"):
            st.write(sup.get("KEYWORDS","—"))

    with st.expander("📋 Full Raw Package"):
        st.markdown(st.session_state.package)

    sc = st.session_state.scenes
    n  = len(sc)

    if n > 0:
        st.markdown(f"""
        <div class="mrow">
          <div class="mbox"><div class="v">{n}</div><div class="l">Scenes</div></div>
          <div class="mbox"><div class="v">1.5x</div><div class="l">Voice Speed</div></div>
          <div class="mbox"><div class="v">👨‍⚕️</div><div class="l">Dr. Aarav</div></div>
          <div class="mbox"><div class="v">₹0</div><div class="l">Cost</div></div>
        </div>""", unsafe_allow_html=True)

        with st.expander("🎬 Story Arc Preview"):
            for i, s in enumerate(sc):
                emoji = PHASE_EMOJI.get(s["phase"],"⚪")
                c1,c2,c3 = st.columns([1,1,3])
                c1.markdown(f"**{i+1}**")
                c2.markdown(emoji + " `" + s["phase"] + "`")
                c3.write(s["hindi"])
                st.divider()
    else:
        st.error("⚠️ 0 scenes parsed. Showing raw output:")
        st.code(st.session_state.raw_llm[:1500])
        st.info("💡 Click Generate again — AI sometimes changes format.")


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2 — PRODUCTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.scenes:
    st.markdown('<div class="card"><span class="badge">STAGE 2 — FULL PRODUCTION ENGINE</span>', unsafe_allow_html=True)

    st.info(
        "👨‍⚕️ Dr. Aarav mascot · 🏥 Clinic branding · 🎨 16 cartoons · "
        "🎙️ 1.5x Madhur voice · 📦 Full ZIP package auto-download"
    )

    if st.button("🎬 LAUNCH FULL PRODUCTION — AUTO PACKAGE & DOWNLOAD"):
        st.session_state.production_running = True
        topic_slug = re.sub(r'[^a-zA-Z0-9]','_',topic)[:20]
        folder = make_project_folder(topic_slug)

        scenes = st.session_state.scenes
        total  = len(scenes)
        sup    = st.session_state.supervised

        prog   = st.progress(0, text="🚀 Production starting...")
        clips, audios = [], []

        # Branding values
        cn = st.session_state.clinic_name
        dn = st.session_state.doctor_name
        a1 = st.session_state.address1
        a2 = st.session_state.address2
        a3 = st.session_state.address3
        ph = st.session_state.phone

        try:
            # ── SCENE LOOP ────────────────────────────────────────────
            for idx, sc in enumerate(scenes):
                pct   = int(idx/total*72)
                emoji = PHASE_EMOJI.get(sc["phase"],"⚪")
                prog.progress(pct, text=f"⚙️ Scene {idx+1}/{total}: {sc['phase'].upper()}...")

                # 1. Cartoon frame with mascot + branding
                logbox.write(f"🎨 {emoji} [{sc['phase']}] Drawing: {sc['keyword']}...")
                img_path = build_frame(sc["keyword"],sc["phase"],idx,total,
                                       folder,cn,dn,a1,a2,a3,ph)
                logbox.write(f"   ✅ Frame saved.")

                # 2. Voice 1.5x
                logbox.write(f"🎙️ Voice: {sc['hindi'][:40]}...")
                aud_path = os.path.join(folder,"audio",f"s{idx}.mp3")
                asyncio.run(tts(sc["hindi"], aud_path))
                dur = get_dur(aud_path)
                logbox.write(f"   ✅ {dur:.1f}s audio.")

                # 3. Ken Burns
                clip = ken_burns(img_path, dur, idx, folder)
                if clip is None:
                    logbox.write(f"   ⚠️ Animation failed scene {idx+1}, skipping.")
                    continue

                # 4. Subtitles
                if add_subs:
                    clip = burn_sub(clip, sc["hindi"], idx, folder)

                clips.append(clip); audios.append(aud_path)

                # 5. Preview
                if show_prev:
                    ptitle = emoji + " Scene " + str(idx+1) + " — " + sc["keyword"]
                    with st.expander(ptitle, expanded=False):
                        st.image(img_path, caption=sc["hindi"][:60])

                logbox.write(f"✅ Scene {idx+1} complete.")

            if not clips:
                st.error("❌ No clips produced. Please try again.")
                st.stop()

            # ── STITCH ────────────────────────────────────────────────
            prog.progress(75, text="🔗 Stitching story...")
            raw_vid = os.path.join(folder,"clips","video_raw.mp4")
            concat_ts(clips, raw_vid)
            logbox.write("✅ Video stitched.")

            prog.progress(82, text="🔊 Merging audio...")
            fin_aud = os.path.join(folder,"audio","final_audio.mp3")
            concat_aud(audios, fin_aud)
            logbox.write("✅ Audio merged.")

            prog.progress(88, text="🎨 Cinematic grade + branding...")
            ts       = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            vid_name = f"DrVasu_{topic_slug}_{ts}.mp4"
            vid_out  = os.path.join(folder,"video",vid_name)
            final_render(raw_vid, fin_aud, vid_out)
            logbox.write("✅ Final render done.")

            # ── THUMBNAILS ────────────────────────────────────────────
            prog.progress(92, text="🖼️ Generating thumbnails...")
            thumb_texts = sup.get("THUMBNAIL_TEXTS","").split("\n")[:3]
            for ti, tt in enumerate(thumb_texts):
                tt = re.sub(r'^\d+[\.\)]\s*','',tt).strip()
                if tt:
                    create_thumbnail(tt[:30], sup.get("HOOK_LINE","")[:40],
                                     (255,60,60) if ti==0 else (255,215,0) if ti==1 else (0,200,120),
                                     folder)
            logbox.write("✅ Thumbnails created.")

            # ── ZIP PACKAGE ───────────────────────────────────────────
            prog.progress(96, text="📦 Creating full ZIP package...")
            zip_path = create_zip(folder, sup, topic)
            st.session_state.output_zip = zip_path
            logbox.write("✅ ZIP package ready.")

            prog.progress(100, text="✅ ALL DONE!")
            st.session_state.production_running = False

            # ── DELIVERY ─────────────────────────────────────────────
            if os.path.exists(vid_out) and os.path.getsize(vid_out) > 10000:
                st.balloons()
                st.success("🏥 Full Package Ready — Video + Thumbnails + Content!")

                # Video preview
                st.video(vid_out)

                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    with open(vid_out,"rb") as f:
                        st.download_button(
                            "📥 DOWNLOAD VIDEO",
                            f, file_name=vid_name, mime="video/mp4",
                            use_container_width=True
                        )
                with col2:
                    with open(zip_path,"rb") as f:
                        st.download_button(
                            "📦 DOWNLOAD FULL ZIP PACKAGE",
                            f,
                            file_name=os.path.basename(zip_path),
                            mime="application/zip",
                            use_container_width=True
                        )

                dur_t = sum(get_dur(a) for a in audios)
                size  = os.path.getsize(vid_out)/1024/1024
                zip_s = os.path.getsize(zip_path)/1024/1024

                st.markdown(f"""
                <div class="mrow">
                  <div class="mbox"><div class="v">{len(clips)}</div><div class="l">Scenes</div></div>
                  <div class="mbox"><div class="v">{dur_t:.0f}s</div><div class="l">Duration</div></div>
                  <div class="mbox"><div class="v">{size:.1f}MB</div><div class="l">Video Size</div></div>
                  <div class="mbox"><div class="v">{zip_s:.1f}MB</div><div class="l">ZIP Size</div></div>
                  <div class="mbox"><div class="v">FREE</div><div class="l">Cost</div></div>
                </div>""", unsafe_allow_html=True)

                # Show folder structure
                st.markdown("### 📁 Package Contents")
                st.markdown(f"""
                ```
                {os.path.basename(folder)}/
                ├── 📹 video/      → {vid_name}
                ├── 🖼️ thumbnails/ → {len(os.listdir(os.path.join(folder,'thumbnails')))} thumbnails
                ├── 🎨 frames/     → {len(clips)} cartoon frames
                ├── 📝 content/    → hashtags, caption, keywords, full_package
                ├── 🔊 audio/      → {len(audios)} voice files
                └── 🏥 branding/   → clinic brand assets
                ```
                """)
            else:
                st.error("⚠️ Video missing. Check logs above.")

        except Exception as e:
            import traceback
            st.session_state.production_running = False
            st.error(f"⚠️ Error: {e}")
            st.code(traceback.format_exc())

    st.markdown("</div>", unsafe_allow_html=True)
