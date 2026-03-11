import streamlit as st
import os
from groq import Groq

# UI Styling
st.set_page_config(page_title="GURJAS V82 STUDIO", page_icon="🎬", layout="centered")
st.title("🎬 GURJAS V82: AGENTIC STUDIO")

# Secrets Management (Security)
GROQ_KEY = st.secrets["GROQ_KEY"]
PEXELS_KEY = st.secrets["PEXELS_KEY"]
client = Groq(api_key=GROQ_KEY)

# --- AGENTIC WORKFLOW ---
niche = st.text_input("Enter Topic (e.g., Silent Heart Attack):", placeholder="Silent Heart Attack...")

if st.button("🚀 START AGENTIC FLOW"):
    # AGENT 1: The Researcher (Fact Check)
    with st.status("🔬 Agent Researcher is scanning medical data...", expanded=True) as status:
        research_prompt = f"Act as a Cardiac Physician. Research 3 deep medical facts about {niche}. Keep it short."
        res = client.chat.completions.create(messages=[{"role": "user", "content": research_prompt}], model="llama-3.3-70b-versatile")
        research_data = res.choices[0].message.content
        st.write("✅ Research Complete")
        
        # AGENT 2: The Script Writer (Viral Hook)
        st.write("✍️ Agent Script-Writer is drafting the viral hook...")
        script_prompt = f"Based on this research: {research_data}, write a high-tension 30-second Hinglish script. Start with a shocker. End with Dr. Vasu Memorial Clinic CTA."
        script_res = client.chat.completions.create(messages=[{"role": "user", "content": script_prompt}], model="llama-3.3-70b-versatile")
        final_script = script_res.choices[0].message.content
        st.write("✅ Script Ready")
        
        status.update(label="🏥 Video Studio Ready!", state="complete", expanded=False)

    st.subheader("Final Viral Script:")
    st.info(final_script)
    st.success("Now you can copy this or use Phase 3 to Render (Cloud integration pending).")
