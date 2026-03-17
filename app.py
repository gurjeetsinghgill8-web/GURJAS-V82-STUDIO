"""
╔══════════════════════════════════════════════════════════════════════════╗
║  GURJAS V14 FINAL — COMPLETE CLOUD AI CONTENT FACTORY                    ║
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
# PAGE CONFIG & CSS
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="GURJAS V14 | Dr. Vasu Factory", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

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
.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:rgba(255,255,255,.04)!important;border:1px solid rgba(255,215,0,.22)!important;border-radius:8px!important;color:#fff!important;}
.mrow{display:flex;gap:.9rem;margin:1rem 0;flex-wrap:wrap;}
.mbox{flex:1;min-width:90px;background:rgba(255,215,0,.06);border:1px solid rgba(255,215,0,.18);border-radius:9px;padding:1rem;text-align:center;}
.mbox .v{font-family:'Cinzel',serif;font-size:1.8rem;color:#FFD700;font-weight:700;}
.mbox .l{font-size:.7rem;color:#556;text-transform:uppercase;letter-spacing:.14em;margin-top:.2rem;}
.arc-row{display:flex;gap:6px;margin:.8rem 0;align-items:center;flex-wrap:wrap;}
.arc-step{padding:5px 14px;border-radius:20px;font-size:.78rem;font-weight:600;}
[data-testid="stSidebar"]{background:rgba(3,6,14,.96);border-right:1px solid rgba(255,215,0,.1);}
.agent-box{background:rgba(0,80,40,.15);border:1px solid rgba(0,200,100,.25);border-radius:10px;padding:1rem 1.2rem;margin:.6rem 0;font-size:.92rem;}
.brand-preview{background:rgba(20,15,0,.8);border:1px solid rgba(255,215,0,.3);border-radius:8px;padding:.8rem 1rem;margin:.4rem 0;font-size:.85rem;font-family:'Rajdhani',sans-serif;color:#FFD700;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hdr"><h1>🏥 GURJAS V14</h1><p>Dr. Vasu AI Cloud Studio · Realistic Graphics · Full Package</p></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# INIT & STATE
# ═══════════════════════════════════════════════════════════════════════════
try:
    client = Groq(api_key=st.secrets["GROQ_KEY"])
except Exception:
    st.error("🚨 GROQ_KEY missing in Streamlit Secrets!")
    st.stop()

PROJECT_BASE = "gurjas_output"
W, H = 1080, 1920

DEFAULTS = {
    "package": "", "scenes": [], "angles": "", "raw_llm": "", "supervised": {}, "production_running": False, "output_zip": "",
    "clinic_name": "Dr. Vasu Memorial Clinic", "doctor_name": "Dr. G.S. Gill", "address1": "Modinagar", "address2": "Evening OPD - Affordable Care", "address3": "", "phone": ""
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

def make_project_folder(topic_slug):
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = re.sub(r'[^a-zA-Z0-9]', '_', topic_slug)[:20]
    folder = os.path.join(PROJECT_BASE, f"{slug}_{ts}")
    for sub in ["video", "thumbnails", "frames", "content", "branding", "audio", "clips", "raw_images"]:
        os.makedirs(os.path.join(folder, sub), exist_ok=True)
    return folder

def lc(c1, c2, t): return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def get_font(size=36):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]:
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()

# ═══════════════════════════════════════════════════════════════════════════
# AGENT LOGIC
# ═══════════════════════════════════════════════════════════════════════════
def run_supervisor(topic, user_story, num_scenes, phase_list):
    has_user_story = len(user_story.strip()) > 30
    instruction = f"The user provided THEIR OWN STORY:\n{user_story}\nENHANCE it into a {num_scenes}-scene script. DO NOT replace it." if has_user_story else f"Create a VIRAL SUSPENSE medical story from scratch for: {topic}. Make it shocking."
    phases_str = "\n".join([f"Scene {i+1}: {p.upper()}" for i, p in enumerate(phase_list)])
    prompt = f"You are a SUPERVISOR AGENT.\n{instruction}\nSTORY STRUCTURE:\n{phases_str}\nOUTPUT FORMAT:\n[SUPERVISOR_NOTES]\nWrite 2-3 lines.\n[HOOK_LINE]\nShocking Hindi line.\n[CAPTION]\nHindi caption.\n[HASHTAGS]\n25 tags.\n[KEYWORDS]\n10 keywords.\n[THUMBNAIL_TEXTS]\n3 options.\n[SCENES]\nWrite exactly {num_scenes} scene lines. FORMAT: SCENE N | [PHASE] | [English keyword] | [Hindi dialogue]\n[END]"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", max_tokens=4500)
    return res.choices[0].message.content

def parse_supervisor_output(raw):
    res = {}
    sections = ["SUPERVISOR_NOTES", "HOOK_LINE", "CAPTION", "HASHTAGS", "KEYWORDS", "THUMBNAIL_TEXTS", "SCENES"]
    for i, sec in enumerate(sections):
        m = re.search(r'\[' + sec + r'\](.*?)(?=\[' + (sections[i+1] if i+1 < len(sections) else 'END') + r'\]|\[END\]|$)', raw, re.DOTALL | re.IGNORECASE)
        res[sec] = m.group(1).strip() if m else ""
    return res

def parse_scenes(raw_text, fallback_phases):
    scenes = []
    VALID_PHASES = {"hook","mystery","clue","rising","reveal","resolution"}
    matches = re.findall(r'SCENE\s*\d*\s*\|\s*([A-Za-z]+)\s*\|\s*([^|\n]+?)\s*\|\s*([^\n]+)', raw_text, re.IGNORECASE)
    if matches:
        for m in matches: scenes.append({"phase": m[0].strip().lower() if m[0].strip().lower() in VALID_PHASES else "clue", "keyword": m[1].strip(), "hindi": m[2].strip()})
        return scenes
    lines = [l.strip() for l in raw_text.split("\n") if "|" in l and len(l) > 20]
    for i, line in enumerate(lines[:12]):
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) >= 3: scenes.append({"phase": fallback_phases[i] if i < len(fallback_phases) else "clue", "keyword": parts[-2], "hindi": parts[-1]})
    return scenes

def build_phase_list(n):
    return (["hook","mystery","clue","rising","clue","rising","clue","rising","reveal","reveal","resolution","resolution"] + ["clue","rising"]*6)[:n]

MOODS = {"hook":{"ac":(255,60,60),"tx":(255,200,200)}, "mystery":{"ac":(140,80,255),"tx":(210,180,255)}, "clue":{"ac":(40,160,255),"tx":(180,220,255)}, "rising":{"ac":(255,160,0),"tx":(255,230,170)}, "reveal":{"ac":(0,220,120),"tx":(180,255,210)}, "resolution":{"ac":(255,215,0),"tx":(255,240,180)}}
PHASE_EMOJI  = {"hook":"🔴","mystery":"🟣","clue":"🔵","rising":"🟠","reveal":"🟢","resolution":"🏆"}
PHASE_LABELS = {"hook":"HOOK — DANGER","mystery":"MYSTERY — SUSPENSE","clue":"CLUE — EVIDENCE","rising":"RISING — TENSION","reveal":"REVEAL — THE TRUTH","resolution":"RESOLUTION — SOLUTION"}
PHASE_BAR    = {"hook":(70,0,0),"mystery":(25,0,70),"clue":(0,25,70),"rising":(70,35,0),"reveal":(0,55,25),"resolution":(55,45,0)}

# ═══════════════════════════════════════════════════════════════════════════
# CLOUD IMAGE API & GRAPHICS
# ═══════════════════════════════════════════════════════════════════════════
def fetch_cloud_ai_image(keyword, phase, folder, idx):
    ai_prompt = f"Highly realistic professional medical 3D render of {keyword}, premium hospital aesthetic, cinematic lighting, dark background, 8k resolution, photorealistic, no text"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(ai_prompt)}?width=1080&height=1920&nologo=true&seed={idx*100}"
    save_path = os.path.join(folder, "raw_images", f"raw_ai_{idx}.jpg")
    try:
        response = requests.get(url, timeout=45)
        if response.status_code == 200:
            with open(save_path, 'wb') as f: f.write(response.content)
            return Image.open(save_path).convert("RGBA")
    except Exception as e: print(f"API failed: {e}")
    return Image.new("RGBA", (1080, 1920), (10, 15, 25, 255))

def draw_doctor_mascot(draw, text_hint="", ac=(255,215,0)):
    bx, by = W - 260, H - 320   
    draw.rounded_rectangle([bx-55,by-290,bx+55,by-110],radius=18,fill=(240,240,255))
    draw.polygon([(bx-55,by-290),(bx-15,by-290),(bx-15,by-200),(bx-55,by-240)],fill=(220,220,240))
    draw.polygon([(bx+55,by-290),(bx+15,by-290),(bx+15,by-200),(bx+55,by-240)],fill=(220,220,240))
    draw.rectangle([bx-8,by-270,bx+8,by-230], fill=(220,40,40))
    draw.rectangle([bx-20,by-258,bx+20,by-242],fill=(220,40,40))
    draw.ellipse([bx-52,by-420,bx+52,by-310],fill=(255,210,170))
    draw.ellipse([bx-52,by-420,bx+52,by-365],fill=(60,40,20))
    draw.ellipse([bx-28,by-390,bx-10,by-372],fill=(255,255,255))
    draw.ellipse([bx+10,by-390,bx+28,by-372],fill=(255,255,255))
    draw.ellipse([bx-21,by-383,bx-17,by-379],fill=(0,0,0))
    draw.ellipse([bx+17,by-383,bx+21,by-379],fill=(0,0,0))
    draw.rounded_rectangle([bx-48,by-428,bx+48,by-412],radius=6,fill=(255,255,255))
    draw.rounded_rectangle([bx+55,by-280,bx+80,by-160],radius=12,fill=(240,240,255))
    draw.ellipse([bx+48,by-155,bx+86,by-125],fill=(255,210,170))
    draw.rounded_rectangle([bx+60,by-125,bx+74,by-75],radius=8,fill=(255,210,170))
    draw.polygon([(bx+67,by-60),(bx+50,by-88),(bx+84,by-88)],fill=ac)

def draw_branding_plate(draw, clinic_name, doctor_name, addr1, addr2, addr3, phone):
    px, py, pw, ph = 30, H - 380, 380, 340
    draw.rounded_rectangle([px, py, px+pw, py+ph], radius=16, fill=(0,0,0, 230))
    draw.rounded_rectangle([px+2, py+2, px+pw-2, py+ph-2], radius=14, fill=(8,8,20, 230))
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

def build_frame(keyword, phase, idx, total, folder, clinic_name, doctor_name, addr1, addr2, addr3, phone):
    mood = MOODS.get(phase, MOODS["clue"])
    base_img = fetch_cloud_ai_image(keyword, phase, folder, idx)
    img = Image.alpha_composite(base_img, Image.new("RGBA", (W, H), (0, 0, 0, 90)))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,112], fill=PHASE_BAR.get(phase,(20,20,50)) + (220,))
    label = PHASE_LABELS.get(phase, phase.upper())
    f = get_font(38)
    try: tw = draw.textbbox((0,0), label, font=f)[2] - draw.textbbox((0,0), label, font=f)[0]
    except: tw = len(label)*20
    draw.text(((W-tw)//2, 33), label, fill=mood["ac"], font=f)
    draw.rectangle([0,H-130,W,H], fill=tuple(max(0,c//5) for c in mood["ac"]) + (220,))
    kw_disp = keyword.upper()[:32]
    f2 = get_font(32)
    try: tw2 = draw.textbbox((0,0), kw_disp, font=f2)[2] - draw.textbbox((0,0), kw_disp, font=f2)[0]
    except: tw2 = len(kw_disp)*17
    draw.text(((W-tw2)//2, H-105), kw_disp, fill=mood["tx"], font=f2)
    for d in range(total):
        dx = W//2-(total*28)//2+d*28+14
        draw.ellipse([dx-9,H-48-9,dx+9,H-48+9], fill=mood["ac"] if d==idx else (100,100,100,150))
    draw_branding_plate(draw, clinic_name, doctor_name, addr1, addr2, addr3, phone)
    draw_doctor_mascot(draw, PHASE_LABELS.get(phase,"").split("—")[0].strip()[:18], mood["ac"])
    out = img.convert("RGB")
    path = os.path.join(folder, "frames", f"s{idx}_ai_frame.png")
    out.save(path)
    return path

def create_thumbnail(title_text, subtitle, ac, folder):
    TW, TH = 1280, 720
    img = Image.new("RGB", (TW, TH))
    draw = ImageDraw.Draw(img)
    for y in range(TH): draw.line([(0,y),(TW,y)], fill=lc((20,0,0), (0,0,20), y/TH))
    draw.polygon([(0,0),(TW//2,0),(0,TH//2)], fill=tuple(max(0,c//4) for c in ac))
    for r in range(300,0,-20): draw.ellipse([TW//2-r,TH//2-r,TW//2+r,TH//2+r], fill=tuple(int(c * (1 - r/300) * 0.3) for c in ac))
    f_title, f_sub = get_font(80), get_font(44)
    words = title_text[:40].upper()
    try: tw = draw.textbbox((0,0), words, font=f_title)[2] - draw.textbbox((0,0), words, font=f_title)[0]
    except: tw = len(words)*44
    draw.text(((TW-tw)//2+4, TH//2-90+4), words, fill=(0,0,0), font=f_title)
    draw.text(((TW-tw)//2, TH//2-90), words, fill=ac, font=f_title)
    sub = subtitle[:50]
    try: tw2 = draw.textbbox((0,0), sub, font=f_sub)[2] - draw.textbbox((0,0), sub, font=f_sub)[0]
    except: tw2 = len(sub)*24
    draw.text(((TW-tw2)//2, TH//2+20), sub, fill=(255,255,255), font=f_sub)
    draw.rectangle([0,TH-70,TW,TH], fill=(0,0,0))
    draw.text((20, TH-56), "DR. VASU MEMORIAL CLINIC", fill=(255,215,0), font=get_font(32))
    path = os.path.join(folder, "thumbnails", f"thumb_{int(time.time())}.png")
    img.save(path)
    return path

# ═══════════════════════════════════════════════════════════════════════════
# MEDIA PROCESSING
# ═══════════════════════════════════════════════════════════════════════════
async def tts(text, path): await edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+50%", pitch="-12Hz").save(path)

def get_dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",path],capture_output=True,text=True)
    try: return max(float(r.stdout.strip()),2.0)
    except: return 3.5

def ken_burns(img, dur, idx, folder):
    out = os.path.join(folder,"clips",f"kb_{idx}.ts")
    frames = max(int(dur*25),55)
    cmd = (f'ffmpeg -y -loop 1 -i "{img}" -vf "zoompan=z=\'min(zoom+0.0020,1.60)\':d={frames}:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=1080x1920:fps=25,scale=1080:1920" -t {dur:.3f} -c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning')
    subprocess.run(cmd,shell=True)
    return out if(os.path.exists(out) and os.path.getsize(out)>500) else None

def burn_sub(clip, text, idx, folder):
    out = os.path.join(folder,"clips",f"sub_{idx}.ts")
    safe = re.sub(r'[\"\':\\%<>]',' ',text)[:70]
    cmd = (f'ffmpeg -y -i "{clip}" -vf "drawtext=text=\'{safe}\':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=h-210:box=1:boxcolor=black@0.75:boxborderw=20" -c:v libx264 -preset ultrafast -pix_fmt yuv420p -an "{out}" -loglevel warning')
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
    cmd = (f'ffmpeg -y -i "{vid}" -i "{aud}" -filter_complex "[0:v]vignette=PI/5[v1];[v1]eq=contrast=1.12:brightness=0.03:saturation=1.2[v2];[v2]drawbox=y=0:x=0:w=iw:h=112:color=black@0.9:t=fill[v3];[v3]drawtext=text=\'DR. VASU MEMORIAL CLINIC\':fontcolor=#FFD700:fontsize=42:x=(w-text_w)/2:y=33[vf]" -map "[vf]" -map 1:a -c:v libx264 -preset fast -c:a aac -b:a 192k -shortest -movflags +faststart "{out}" -loglevel warning')
    subprocess.run(cmd,shell=True)

def create_zip(folder, supervised, topic):
    zip_path = folder + ".zip"
    content_dir = os.path.join(folder,"content")
    with open(os.path.join(content_dir,"full_package.txt"),"w",encoding="utf-8") as f:
        f.write(f"Topic: {topic}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{'='*50}\n")
        for key, val in supervised.items(): f.write(f"\n[{key}]\n{val}\n")
    with open(os.path.join(content_dir,"hashtags.txt"),"w",encoding="utf-8") as f: f.write(supervised.get("HASHTAGS",""))
    with open(os.path.join(content_dir,"caption.txt"),"w",encoding="utf-8") as f: f.write(supervised.get("CAPTION",""))
    with open(os.path.join(content_dir,"keywords.txt"),"w",encoding="utf-8") as f: f.write(supervised.get("KEYWORDS",""))
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder):
            for file in files: zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.dirname(folder)))
    return zip_path

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🏥 CLINIC BRANDING")
    st.session_state.clinic_name = st.text_input("Clinic Name:", value=st.session_state.clinic_name)
    st.session_state.doctor_name = st.text_input("Doctor Name:", value=st.session_state.doctor_name)
    st.session_state.address1    = st.text_input("Address Line 1:", value=st.session_state.address1)
    st.session_state.address2    = st.text_input("Address Line 2:", value=st.session_state.address2)
    st.session_state.address3    = st.text_input("City:", value=st.session_state.address3)
    st.session_state.phone       = st.text_input("Phone (optional):", value=st.session_state.phone)
    st.markdown(f'<div class="brand-preview">🏥 <b>{st.session_state.clinic_name}</b><br>👨‍⚕️ {st.session_state.doctor_name}<br>📍 {st.session_state.address1}<br>{st.session_state.address2}<br>{st.session_state.address3}<br>{"📞 " + st.session_state.phone if st.session_state.phone else ""}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ⚙️ VIDEO SETTINGS")
    num_scenes = st.slider("📽️ Scenes:", 5, 12, 7)
    add_subs   = st.checkbox("📝 Hindi Subtitles", True)
    show_prev  = st.checkbox("🖼️ Show Frame Previews", True)
    st.markdown("---")
    st.markdown("### 🛠️ Live Production Log")
    logbox = st.empty()

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1 — CONTENT INPUT
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card"><span class="badge">STAGE 1 — SUPERVISOR AGENT</span>', unsafe_allow_html=True)
topic = st.text_input("💉 Medical Topic:", placeholder="e.g. Heart Failure ke 3 khamoosh signs")
user_story = st.text_area("✍️ Apni Story (Optional):", placeholder="Agar aap khud ki story denge toh Agent isse enhance karega...", height=120)

if st.button("⚡ SUPERVISOR AGENT — GENERATE PACKAGE"):
    if not topic.strip(): st.warning("Please enter a medical topic.")
    else:
        with st.status("🤖 Supervisor Agent working...", expanded=True) as status:
            phase_list = build_phase_list(num_scenes)
            raw = run_supervisor(topic, user_story, num_scenes, phase_list)
            st.session_state.raw_llm = raw
            st.session_state.package = raw
            supervised = parse_supervisor_output(raw)
            st.session_state.supervised = supervised
            scenes = parse_scenes(supervised.get("SCENES","") or raw, phase_list)
            st.session_state.scenes = scenes
            status.update(label=f"✅ Agent done! {len(scenes)} scenes ready.", state="complete")
st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.supervised and len(st.session_state.scenes) > 0:
    sup = st.session_state.supervised
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🎣 Hook Line"): st.write(sup.get("HOOK_LINE","—"))
        with st.expander("📝 Caption"): st.write(sup.get("CAPTION","—"))
    with col2:
        with st.expander("#️⃣ Hashtags"): st.write(sup.get("HASHTAGS","—"))
        with st.expander("🔑 Keywords"): st.write(sup.get("KEYWORDS","—"))

# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2 — PRODUCTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════
if st.session_state.scenes:
    st.markdown('<div class="card"><span class="badge">STAGE 2 — FULL PRODUCTION ENGINE</span>', unsafe_allow_html=True)
    
    if st.button("🎬 LAUNCH FULL PRODUCTION — AUTO PACKAGE & DOWNLOAD"):
        st.session_state.production_running = True
        topic_slug = re.sub(r'[^a-zA-Z0-9]','_',topic)[:20]
        folder = make_project_folder(topic_slug)
        scenes, total, sup = st.session_state.scenes, len(st.session_state.scenes), st.session_state.supervised
        prog = st.progress(0, text="🚀 Production starting...")
        clips, audios = [], []
        cn, dn, a1, a2, a3, ph = st.session_state.clinic_name, st.session_state.doctor_name, st.session_state.address1, st.session_state.address2, st.session_state.address3, st.session_state.phone

        try:
            for idx, sc in enumerate(scenes):
                prog.progress(int(idx/total*72), text=f"⚙️ Scene {idx+1}/{total}: fetching AI Image...")
                logbox.write(f"🎨 Getting AI image for: {sc['keyword']}...")
                img_path = build_frame(sc["keyword"],sc["phase"],idx,total,folder,cn,dn,a1,a2,a3,ph)
                logbox.write(f"🎙️ Generating Voice...")
                aud_path = os.path.join(folder,"audio",f"s{idx}.mp3")
                asyncio.run(tts(sc["hindi"], aud_path))
                dur = get_dur(aud_path)
                clip = ken_burns(img_path, dur, idx, folder)
                if clip:
                    if add_subs: clip = burn_sub(clip, sc["hindi"], idx, folder)
                    clips.append(clip); audios.append(aud_path)
                if show_prev:
                    with st.expander(f"Scene {idx+1} — {sc['keyword']}", expanded=False): st.image(img_path, caption=sc["hindi"][:60])
                logbox.write(f"✅ Scene {idx+1} complete.")

            if clips:
                prog.progress(75, text="🔗 Stitching video & audio...")
                raw_vid, fin_aud = os.path.join(folder,"clips","video_raw.mp4"), os.path.join(folder,"audio","final_audio.mp3")
                concat_ts(clips, raw_vid); concat_aud(audios, fin_aud)
                
                prog.progress(88, text="🎨 Final render...")
                vid_name = f"DrVasu_{topic_slug}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.mp4"
                vid_out = os.path.join(folder,"video",vid_name)
                final_render(raw_vid, fin_aud, vid_out)
                
                prog.progress(92, text="🖼️ Thumbnails...")
                for ti, tt in enumerate(sup.get("THUMBNAIL_TEXTS","").split("\n")[:3]):
                    if re.sub(r'^\d+[\.\)]\s*','',tt).strip(): create_thumbnail(re.sub(r'^\d+[\.\)]\s*','',tt).strip()[:30], sup.get("HOOK_LINE","")[:40], (255,60,60) if ti==0 else (255,215,0), folder)
                
                prog.progress(96, text="📦 Zipping package...")
                zip_path = create_zip(folder, sup, topic)
                prog.progress(100, text="✅ ALL DONE!")
                
                if os.path.exists(vid_out) and os.path.getsize(vid_out) > 10000:
                    st.balloons(); st.success("🏥 Full Package Ready!")
                    st.video(vid_out)
                    c1, c2 = st.columns(2)
                    with c1: st.download_button("📥 DOWNLOAD VIDEO", open(vid_out,"rb"), file_name=vid_name, mime="video/mp4", use_container_width=True)
                    with c2: st.download_button("📦 DOWNLOAD ZIP", open(zip_path,"rb"), file_name=os.path.basename(zip_path), mime="application/zip", use_container_width=True)
            else: st.error("❌ No clips produced.")
        except Exception as e:
            import traceback
            st.error(f"⚠️ Error: {e}"); st.code(traceback.format_exc())
    st.markdown("</div>", unsafe_allow_html=True)
