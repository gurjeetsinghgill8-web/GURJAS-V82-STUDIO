"""
╔══════════════════════════════════════════════════════════════════════════╗
║  GURJAS V14 — DR. VASU CLOUD AI CONTENT FACTORY                          ║
║                                                                          ║
║  NEW IN V14:                                                             ║
║  • Cloud Image API   — Ultra-realistic 3D medical backgrounds            ║
║  • Zero Local Load   — Perfect for older laptops (6GB RAM)               ║
║  • Supervisor Agent  — quality check, story protection, keywords         ║
║  • Cartoon Doctor    — human doctor mascot on every scene                ║
║  • Multi-Clinic      — custom branding plate bottom-left                 ║
║  • Full ZIP Package  — video + thumbnails + content + branding           ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import os, asyncio, subprocess, shutil, re, time, math, zipfile
from datetime import datetime
import edge_tts
import requests
import urllib.parse
from groq import Groq
from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GURJAS V14 | Dr. Vasu Factory",
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
  <h1>🏥 GURJAS V14</h1>
  <p>Dr. Vasu AI Cloud Studio &nbsp;·&nbsp; Realistic Graphics &nbsp;·&nbsp; Full Package</p>
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
    "clinic_name": "Dr. Vasu Memorial Clinic",
    "doctor_name": "Dr. G.S. Gill",
    "address1": "Modinagar",
    "address2": "Evening OPD - Affordable Care",
    "address3": "",
    "phone": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def make_project_folder(topic_slug):
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = re.sub(r'[^a-zA-Z0-9]', '_', topic_slug)[:20]
    folder = os.path.join(PROJECT_BASE, f"{slug}_{ts}")
    for sub in ["video", "thumbnails", "frames", "content", "branding", "audio", "clips", "raw_images"]:
        os.makedirs(os.path.join(folder, sub), exist_ok=True)
    return folder

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════
W, H = 1080, 1920

def lc(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

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
    has_user_story = len(user_story.strip()) > 30

    if has_user_story:
        instruction = f"The user has provided THEIR OWN STORY below. ENHANCE it — keep the core meaning, make it dramatic. DO NOT replace their story.\nUSER'S STORY:\n{user_story}\n\nEnhance into a {num_scenes}-scene script."
    else:
        instruction = f"Create a VIRAL SUSPENSE medical story from scratch for: {topic}. Make it shocking."

    phases_str = "\n".join([f"Scene {i+1}: {p.upper()}" for i, p in enumerate(phase_list)])

    prompt = f"""You are a SUPERVISOR AGENT for a world-class medical video factory.
{instruction}
STORY STRUCTURE:
{phases_str}

OUTPUT FORMAT:
[SUPERVISOR_NOTES]
Write 2-3 lines about quality decisions.
[HOOK_LINE]
One 5-7 word shocking Hindi opening line.
[CAPTION]
3-4 emotional Hindi lines. End with clinic CTA.
[HASHTAGS]
25 hashtags — mix of Hindi/English medical.
[KEYWORDS]
10 SEO keywords. Comma-separated.
[THUMBNAIL_TEXTS]
3 separate thumbnail text options (4-5 bold Hindi words). Numbered 1-2-3.
[SCENES]
Write exactly {num_scenes} scene lines. STRICT FORMAT:
SCENE [N] | [PHASE] | [English medical keyword 3-5 words] | [Hindi dialogue]
[END]"""

    res = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        max_tokens=4500
    )
    return res.choices[0].message.content


def parse_supervisor_output(raw):
    result = {}
    sections = ["SUPERVISOR_NOTES", "HOOK_LINE", "CAPTION", "HASHTAGS",
                "KEYWORDS", "THUMBNAIL_TEXTS", "SCENES"]
    for i, sec in enumerate(sections):
        pattern = r'\[' + sec + r'\](.*?)(?=\[' + (sections[i+1] if i+1 < len(sections) else 'END') + r'\]|\[END\]|$)'
        m = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        result[sec] = m.group(1).strip() if m else ""
    return result

def parse_scenes(raw_text, fallback_phases):
    scenes = []
    VALID_PHASES = {"hook","mystery","clue","rising","reveal","resolution"}
    matches = re.findall(r'SCENE\s*\d*\s*\|\s*([A-Za-z]+)\s*\|\s*([^|\n]+?)\s*\|\s*([^\n]+)', raw_text, re.IGNORECASE)
    if matches:
        for m in matches:
            phase = m[0].strip().lower()
            if phase not in VALID_PHASES: phase = "clue"
            scenes.append({"phase": phase, "keyword": m[1].strip(), "hindi": m[2].strip()})
        return scenes
    
    lines = [l.strip() for l in raw_text.split("\n") if "|" in l and len(l) > 20]
    for i, line in enumerate(lines[:12]):
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3:
            phase = fallback_phases[i] if i < len(fallback_phases) else "clue"
            scenes.append({"phase": phase, "keyword": parts[-2], "hindi": parts[-1]})
    return scenes

def build_phase_list(n):
    base = ["hook","mystery","clue","rising","clue","rising","clue","rising","reveal","reveal","resolution","resolution"]
    return (base + ["clue","rising"]*6)[:n]

# ═══════════════════════════════════════════════════════════════════════════
# MOOD PALETTES
# ═══════════════════════════════════════════════════════════════════════════
MOODS = {
    "hook":       {"ac":(255,60,60),  "tx":(255,200,200)},
    "mystery":    {"ac":(140,80,255), "tx":(210,180,255)},
    "clue":       {"ac":(40,160,255), "tx":(180,220,255)},
    "rising":     {"ac":(255,160,0),  "tx":(255,230,170)},
    "reveal":     {"ac":(0,220,120),  "tx":(180,255,210)},
    "resolution": {"ac":(255,215,0),  "tx":(255,240,180)},
}
PHASE_EMOJI  = {"hook":"🔴","mystery":"🟣","clue":"🔵","rising":"🟠","reveal":"🟢","resolution":"🏆"}
PHASE_LABELS = {"hook":"HOOK — DANGER","mystery":"MYSTERY — SUSPENSE","clue":"CLUE — EVIDENCE",
                "rising":"RISING — TENSION","reveal":"REVEAL — THE TRUTH","resolution":"RESOLUTION — SOLUTION"}
PHASE_BAR    = {"hook":(70,0,0),"mystery":(25,0,70),"clue":(0,25,70),
                "rising":(70,35,0),"reveal":(0,55,25),"resolution":(55,45,0)}


# ═══════════════════════════════════════════════════════════════════════════
# 🌩️ CLOUD AI IMAGE GENERATOR (REPLACES MS PAINT DRAWINGS)
# ═══════════════════════════════════════════════════════════════════════════
def fetch_cloud_ai_image(keyword, phase, folder, idx):
    """
    Fetches a high-quality, realistic medical image from Pollinations AI.
    No API key required. Perfect for old laptops.
    """
    # Create a highly professional prompt for the AI
    ai_prompt = f"Highly realistic professional medical 3D render of {keyword}, premium hospital aesthetic, cinematic lighting, dark background, 8k resolution, photorealistic, no text"
    
    encoded_prompt = urllib.parse.quote(ai_prompt)
    # Using a random seed based on idx so identical keywords get different images
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&seed={idx*100}"
    
    save_path = os.path.join(folder, "raw_images", f"raw_ai_{idx}.jpg")
    
    try:
        # Fetch the image from the cloud
        response = requests.get(url, timeout=45)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # Open and convert to RGBA for blending overlays later
            return Image.open(save_path).convert("RGBA")
    except Exception as e:
        print(f"Image API failed: {e}")
        pass
        
    # Fallback if internet fails: A sleek dark background
    fallback = Image.new("RGBA", (1080, 1920), (10, 15, 25, 255))
    return fallback


# ═══════════════════════════════════════════════════════════════════════════
# 👨‍⚕️ CARTOON DOCTOR MASCOT (Kept to maintain the brand identity)
# ═══════════════════════════════════════════════════════════════════════════
def draw_doctor_mascot(draw, text_hint="", ac=(255,215,0)):
    bx, by = W - 260, H - 320   
    draw.rounded_rectangle([bx-28,by-120,bx-8,by],  radius=10, fill=(100,120,180))
    draw.rounded_rectangle([bx+8, by-120,bx+28,by],  radius=10, fill=(100,120,180))
    draw.rounded_rectangle([bx-38,by-18,bx,by+10],   radius=8,  fill=(40,40,60))
    draw.rounded_rectangle([bx,   by-18,bx+38,by+10],radius=8,  fill=(40,40,60))
    draw.rounded_rectangle([bx-55,by-290,bx+55,by-110],radius=18,fill=(240,240,255))
    draw.polygon([(bx-55,by-290),(bx-15,by-290),(bx-15,by-200),(bx-55,by-240)],fill=(220,220,240))
    draw.polygon([(bx+55,by-290),(bx+15,by-290),(bx+15,by-200),(bx+55,by-240)],fill=(220,220,240))
    draw.rectangle([bx-8,by-270,bx+8,by-230], fill=(220,40,40))
    draw.rectangle([bx-20,by-258,bx+20,by-242],fill=(220,40,40))
    draw.arc([bx-30,by-230,bx+30,by-170], 180, 0, fill=(60,60,80), width=8)
    draw.ellipse([bx-18,by-174,bx+2,by-158],fill=(60,60,80))
    draw.ellipse([bx+12,by-186,bx+28,by-170],fill=(180,180,200))
    draw.rounded_rectangle([bx-14,by-320,bx+14,by-292],radius=6,fill=(255,210,170))
    draw.ellipse([bx-52,by-420,bx+52,by-310],fill=(255,210,170))
    draw.ellipse([bx-52,by-420,bx+52,by-365],fill=(60,40,20))
    draw.ellipse([bx-45,by-410,bx+45,by-370],fill=(80,55,25))
    draw.ellipse([bx-28,by-390,bx-10,by-372],fill=(255,255,255))
    draw.ellipse([bx+10,by-390,bx+28,by-372],fill=(255,255,255))
    draw.ellipse([bx-24,by-386,bx-14,by-376],fill=(40,80,160))
    draw.ellipse([bx+14,by-386,bx+24,by-376],fill=(40,80,160))
    draw.ellipse([bx-21,by-383,bx-17,by-379],fill=(0,0,0))
    draw.ellipse([bx+17,by-383,bx+21,by-379],fill=(0,0,0))
    draw.arc([bx-30,by-400,bx-8,by-380],200,340,fill=(60,40,20),width=5)
    draw.arc([bx+8, by-400,bx+30,by-380],200,340,fill=(60,40,20),width=5)
    draw.arc([bx-20,by-368,bx+20,by-348],10,170,fill=(180,80,80),width=5)
    draw.ellipse([bx-62,by-388,bx-44,by-366],fill=(255,190,150))
    draw.ellipse([bx+44,by-388,bx+62,by-366],fill=(255,190,150))
    draw.rounded_rectangle([bx-48,by-428,bx+48,by-412],radius=6,fill=(255,255,255))
    draw.rectangle([bx-6,by-445,bx+6,by-428],fill=(255,255,255))
    draw.rectangle([bx-16,by-448,bx+16,by-440],fill=(255,255,255))
    draw.rounded_rectangle([bx-80,by-280,bx-55,by-160],radius=12,fill=(240,240,255))
    draw.ellipse([bx-88,by-175,bx-50,by-145],fill=(255,210,170))
    draw.rounded_rectangle([bx+55,by-280,bx+80,by-160],radius=12,fill=(240,240,255))
    draw.ellipse([bx+48,by-155,bx+86,by-125],fill=(255,210,170))
    draw.rounded_rectangle([bx+60,by-125,bx+74,by-75],radius=8,fill=(255,210,170))
    draw.polygon([(bx+67,by-60),(bx+50,by-88),(bx+84,by-88)],fill=ac)

    if text_hint:
        bubble_x, bubble_y, bubble_w, bubble_h = bx - 280, by - 440, 240, 70
        draw.rounded_rectangle([bubble_x,bubble_y,bubble_x+bubble_w,bubble_y+bubble_h], radius=18,fill=(255,255,255))
        draw.rounded_rectangle([bubble_x+2,bubble_y+2,bubble_x+bubble_w-2,bubble_y+bubble_h-2], radius=16,fill=(255,252,230))
        draw.polygon([(bubble_x+bubble_w,bubble_y+bubble_h-20),(bubble_x+bubble_w+30,bubble_y+bubble_h-10),(bubble_x+bubble_w,bubble_y+bubble_h-40)],fill=(255,252,230))
        draw.polygon([(bubble_x+bubble_w,bubble_y+bubble_h-20),(bubble_x+bubble_w+30,bubble_y+bubble_h-10),(bubble_x+bubble_w,bubble_y+bubble_h-40)],outline=(200,180,100),width=2)
        hint = text_hint[:22]
        f_hint = get_font(24)
        try:
            bb = draw.textbbox((0,0), hint, font=f_hint); tw = bb[2]-bb[0]
        except: tw = len(hint)*13
        draw.text((bubble_x + (bubble_w - tw)//2, bubble_y+18), hint, fill=(40,40,80), font=f_hint)

# ═══════════════════════════════════════════════════════════════════════════
# 🏥 BRANDING PLATE 
# ═══════════════════════════════════════════════════════════════════════════
def draw_branding_plate(draw, clinic_name, doctor_name, addr1, addr2, addr3, phone):
    px, py, pw, ph = 30, H - 380, 380, 340
    draw.rounded_rectangle([px, py, px+pw, py+ph], radius=16, fill=(0,0,0, 230)) # Slight transparency
    draw.rounded_rectangle([px+2, py+2, px+pw-2, py+ph-2], radius=14, fill=(8,8,20, 230))
    for i in range(3):
        draw.rounded_rectangle([px+i, py+i, px+pw-i, py+ph-i], radius=16-i, outline=(255,215,0), width=1)
    draw.rectangle([px+18, py+15, px+28, py+50], fill=(220,40,40))
    draw.rectangle([px+10, py+24, px+36, py+40], fill=(220,40,40))

    f_clinic, f_small, f_tiny = get_font(32), get_font(24), get_font(20)
    draw.text((px+46, py+14), clinic_name[:22], fill=(255,215,0), font=f_clinic)
    draw.line([(px+10, py+58), (px+pw-10, py+58)], fill=(255,215,0), width=2)
    draw.text((px+14, py+68), doctor_name[:28], fill=(200,220,255), font=f_small)

    y_off = py + 104
    for line in [addr1, addr2, addr3]:
        if line.strip():
            draw.text((px+14, y_off), line[:32], fill=(180,180,200), font=f_tiny)
            y_off += 30

    if phone.strip(): draw.text((px+14, y_off+6), "📞 " + phone[:20], fill=(255,215,0), font=f_tiny)
    draw.rounded_rectangle([px+10, py+ph-28, px+pw-10, py+ph-10], radius=8, fill=(255,215,0))
    draw.text((px+14, py+ph-26), "Expert Care · Trusted Results", fill=(0,0,0), font=f_tiny)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN FRAME BUILDER (UPDATED FOR CLOUD IMAGES)
# ═══════════════════════════════════════════════════════════════════════════
def build_frame(keyword, phase, idx, total, folder,
                clinic_name, doctor_name, addr1, addr2, addr3, phone):
    mood = MOODS.get(phase, MOODS["clue"])
    
    # 1. Fetch realistic AI background instead of drawing shapes
    base_img = fetch_cloud_ai_image(keyword, phase, folder, idx)
    
    # Add a slight dark vignette overlay so text and branding stand out
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 90))
    img = Image.alpha_composite(base_img, overlay)
    
    draw = ImageDraw.Draw(img)

    # Top phase bar (slightly transparent)
    draw.rectangle([0,0,W,112], fill=PHASE_BAR.get(phase,(20,20,50)) + (220,))
    label = PHASE_LABELS.get(phase, phase.upper())
    f = get_font(38)
    try:
        bb = draw.textbbox((0,0), label, font=f); tw = bb[2]-bb[0]
    except: tw = len(label)*20
    draw.text(((W-tw)//2, 33), label, fill=mood["ac"], font=f)

    # Bottom keyword bar (slightly transparent)
    draw.rectangle([0,H-130,W,H], fill=tuple(max(0,c//5) for c in mood["ac"]) + (220,))
    kw_disp = keyword.upper()[:32]
    f2 = get_font(32)
    try:
        bb2 = draw.textbbox((0,0), kw_disp, font=f2); tw2 = bb2[2]-bb2[0]
    except: tw2 = len(kw_disp)*17
    draw.text(((W-tw2)//2, H-105), kw_disp, fill=mood["tx"], font=f2)

    # Progress dots
    for d in range(total):
        dx = W//2-(total*28)//2+d*28+14
        draw.ellipse([dx-9,H-48-9,dx+9,H-48+9], fill=mood["ac"] if d==idx else (100,100,100,150))

    # Branding plate
    draw_branding_plate(draw, clinic_name, doctor_name, addr1, addr2, addr3, phone)

    # Doctor mascot
    short_hint = PHASE_LABELS.get(phase,"").split("—")[0].strip()[:18]
    draw_doctor_mascot(draw, short_hint, mood["ac"])

    # Convert back to RGB for video processing
    out = img.convert("RGB")
    path = os.path.join(folder, "frames", f"s{idx}_ai_frame.png")
    out.save(path)
    return path

# ═══════════════════════════════════════════════════════════════════════════
# MEDIA, FFmpeg, AND ZIP LOGIC REMAINS UNCHANGED
# (Omitted full text here for brevity, keep the exact same logic you had in V13 for tts, ken_burns, etc.)
# ═══════════════════════════════════════════════════════════════════════════
async def tts(text, path):
    await edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+50%", pitch="-12Hz").save(path)

def get_dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",path],capture_output=True,text=True)
    try:    return max(float(r.stdout.strip()),2.0)
    except: return 3.5

def ken_burns(img, dur, idx, folder):
    out = os.path.join(folder,"clips",f"kb_{idx}.ts")
    frames = max(int(dur*25),55)
    pats = [("min(zoom+0.0020,1.60)","iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)"),]
    z,x,y = pats[0]
    cmd = (f'ffmpeg -y -loop 1 -i "{img}" '
           f'-vf "zoompan=z=\'{z}\':d={frames}:x=\'{x}\':y=\'{y}\':s=1080x1920:fps=25,scale=1080:1920" '
           f'-t {dur:.3f} -c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning')
    subprocess.run(cmd,shell=True)
    return out if(os.path.exists(out) and os.path.getsize(out)>500) else None

def burn_sub(clip, text, idx, folder):
    out  = os.path.join(folder,"clips",f"sub_{idx}.ts")
    safe = re.sub(r'[\"\':\\%<>]',' ',text)[:70]
    cmd  = (f'ffmpeg -y -i "{clip}" '
            f'-vf "drawtext=text=\'{safe}\':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=h-210:box=1:boxcolor=black@0.75:boxborderw=20" '
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
           f'-filter_complex "[0:v]vignette=PI/5[v1];[v1]eq=contrast=1.12:brightness=0.03:saturation=1.2[v2]" '
           f'-map "[v2]" -map 1:a -c:v libx264 -preset fast '
           f'-c:a aac -b:a 192k -shortest -movflags +faststart "{out}" -loglevel warning')
    subprocess.run(cmd,shell=True)

# (Skipping ZIP function and UI rendering for brevity as they are identical to V13)
# You only need to replace the image generation logic in your Streamlit app!
