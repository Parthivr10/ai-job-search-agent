# -------------------------------
# LOAD ENV
# -------------------------------
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import tempfile
import re
from agent.graph import build_graph



# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Job Agent", layout="wide", page_icon="🤖")

# -------------------------------
# GLOBAL CSS  (styling only — no user data injected into HTML)
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: #0b0f1a !important;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; display: none; }

/* inputs */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #0b0f1a !important;
    font-size: 15px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(99,255,180,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,255,180,0.07) !important;
}
[data-testid="stTextInput"] label {
    color: #63ffb4 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* file uploader */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px dashed rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] label {
    color: #63ffb4 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* search button */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #63ffb4 0%, #38bdf8 100%) !important;
    color: #0b0f1a !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(99,255,180,0.2) !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(99,255,180,0.3) !important;
}

/* link button (Apply Now) */
[data-testid="stLinkButton"] a {
    background: transparent !important;
    border: 1.5px solid rgba(56,189,248,0.45) !important;
    color: #38bdf8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
}
[data-testid="stLinkButton"] a:hover {
    background: rgba(56,189,248,0.08) !important;
}

/* card container */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(99,255,180,0.22) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35) !important;
}

/* caption colour */
[data-testid="stCaptionContainer"] p {
    color: #4a5568 !important;
    font-size: 12px !important;
    letter-spacing: 0.8px !important;
}

/* metric — score badge */
[data-testid="stMetricValue"] {
    font-family: 'Sora', sans-serif !important;
    font-size: 34px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #63ffb4, #38bdf8) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
[data-testid="stMetricLabel"] {
    color: #3d6652 !important;
    font-size: 10px !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
}

/* success chips (matched skills) */
[data-testid="stAlert"][kind="success"],
div[data-baseweb="notification"] {
    border-radius: 100px !important;
    padding: 4px 12px !important;
    font-size: 12px !important;
}

/* divider */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 10px 0 !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0b0f1a; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HERO  (pure static HTML — no user data here)
# -------------------------------
st.markdown("""
<div style="
    background: linear-gradient(135deg,#0d1b3e 0%,#0b0f1a 55%,#0d2b1e 100%);
    border-bottom: 1px solid rgba(99,255,180,0.1);
    padding: 52px 48px 44px;
    margin: -1rem -1rem 0 -1rem;
">
    <div style="display:inline-block;background:rgba(99,255,180,0.1);
        border:1px solid rgba(99,255,180,0.25);color:#63ffb4;font-size:10px;
        font-weight:700;letter-spacing:1.6px;text-transform:uppercase;
        padding:5px 14px;border-radius:100px;margin-bottom:18px;">
        ✦ AI-Powered Matching
    </div>
    <div style="font-family:'Sora',sans-serif;font-size:clamp(28px,4vw,50px);
        font-weight:700;line-height:1.1;color:#f0f6ff;letter-spacing:-1px;">
        Find Your Next Role with<br>
        <span style="background:linear-gradient(90deg,#63ffb4,#38bdf8);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;">
            Smart AI Matching
        </span>
    </div>
    <div style="margin-top:14px;font-size:15px;color:#94a3b8;font-weight:300;
        max-width:500px;line-height:1.6;">
        Describe your dream job, upload your resume — our AI ranks the best
        opportunities based on your real skills.
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# -------------------------------
# CLEAN TEXT HELPER
# -------------------------------
def clean_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text, flags=re.DOTALL)
    text = re.sub(r"&[a-zA-Z#0-9]+;", " ", text)
    text = re.sub(r"[<>]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -------------------------------
# SEARCH PANEL
# -------------------------------
col_q, col_f, col_btn = st.columns([3, 3, 1.2])

with col_q:
    query = st.text_input("🔍  Job Search Query", placeholder="e.g. Gen AI Engineer in Bangalore")

with col_f:
    uploaded_file = st.file_uploader("📄  Upload Resume (PDF)", type=["pdf"])

with col_btn:
    st.write("")
    st.write("")
    search_clicked = st.button("Search Jobs →")

st.divider()

# -------------------------------
# ACTION
# -------------------------------
if search_clicked:

    if not query or not uploaded_file:
        st.warning("⚠️  Please enter a search query and upload your resume to continue.")
        st.stop()

    # Save resume
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        resume_path = tmp.name

    st.success("✅  Resume uploaded — scanning jobs for you…")

    with st.spinner("🤖  AI agent is ranking jobs based on your profile…"):
        # Build agent
        app = build_graph()

        # Run agent
        result = app.invoke({
            "query": query,
            "resume_path": resume_path
        })

    jobs = result.get("ranked_jobs", [])

    if not jobs:
        st.warning("No matching jobs found. Try a different query or broaden your search.")
        st.stop()

    # ── Section heading ──
    st.write("")
    col_h1, col_h2 = st.columns([8, 1])
    with col_h1:
        st.markdown("### 🎯 Top Matches")
    with col_h2:
        st.markdown(
            f"<div style='margin-top:8px;background:rgba(99,255,180,0.1);"
            f"border:1px solid rgba(99,255,180,0.2);color:#63ffb4;font-size:12px;"
            f"font-weight:600;padding:3px 12px;border-radius:100px;"
            f"text-align:center;'>{len(jobs)} results</div>",
            unsafe_allow_html=True
        )
    st.write("")

    # -------------------------------
    # JOB CARDS — pure Streamlit components, zero user-data HTML injection
    # -------------------------------
    for i, job in enumerate(jobs):

        title          = clean_html(job.get("title", "Untitled Role"))
        company        = clean_html(job.get("company", "Company"))
        location       = clean_html(job.get("location", ""))
        posted         = clean_html(job.get("posted", ""))
        score          = job.get("score", 0)
        url            = job.get("url", "#")
        job_skills     = job.get("skills", [])
        matched_skills = job.get("matched_skills", [])

        raw_desc = job.get("description", "")
        desc     = clean_html(raw_desc)
        desc     = desc[:300] + "…" if len(desc) > 300 else desc

        initial = company[0].upper() if company else "?"

        # ── Card ──
        with st.container(border=True):

            # Top row: avatar | title+company+meta | score
            col_logo, col_info, col_score = st.columns([0.6, 6, 1.5])

            with col_logo:
                # Company initial avatar — only the initial letter goes in, fully safe
                st.markdown(
                    f"<div style='width:46px;height:46px;border-radius:12px;"
                    f"background:linear-gradient(135deg,rgba(99,255,180,0.15),rgba(56,189,248,0.15));"
                    f"border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;"
                    f"justify-content:center;font-size:20px;font-weight:700;color:#63ffb4;"
                    f"font-family:Sora,sans-serif;margin-top:2px;'>{initial}</div>",
                    unsafe_allow_html=True
                )

            with col_info:
                # Title — use st.subheader so no HTML needed
                st.subheader(title, divider=False)
                # Company in green using write with colour hack-free approach
                st.write(f"🏢 **{company}**")
                # Meta row — plain text via caption
                meta_parts = []
                if location:
                    meta_parts.append(f"📍 {location}")
                if posted:
                    meta_parts.append(f"🕐 {posted}")
                if meta_parts:
                    st.caption("  ·  ".join(meta_parts))
                salary = job.get("salary", "")
                if salary:
                    st.caption(f"{salary}")    

            with col_score:
                st.metric(label="Match Score", value=f"{score}%")
                if job.get("match_reason"):
                    st.caption(job.get("match_reason"))

            # Description
            if desc:
                st.divider()
                st.write(desc)

            # Matched skills — st.success badges
            if matched_skills:
                st.divider()
                st.caption("✦  MATCHED SKILLS")
                chip_cols = st.columns(min(len(matched_skills), 5))
                for idx, skill in enumerate(matched_skills):
                    with chip_cols[idx % 5]:
                        st.success(f"✓ {skill}")

            # Job skills — plain comma-separated text
            if job_skills:
                st.caption("REQUIRED SKILLS")
                st.write("  ·  ".join(job_skills))

            # Apply button
            st.divider()
            st.link_button("Apply Now →", url=url)

        st.write("")  # spacing between cards