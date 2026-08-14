"""
🎓 CHRIST (Deemed to be University)
🛡️ SENTINEL - Automated Gate Compliance Interface

[FUTURISTIC HUD EDITION]

Run:
    streamlit run app.py
"""

import os
import glob
import uuid
import time
import datetime
import cv2
import pandas as pd
import plotly.express as px
import streamlit as st

from src.compliance_engine import ComplianceEngine

# --- Page & HUD Setup ---
st.set_page_config(
    page_title="SENTINEL // Gate Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CARDS_DIR = os.path.join(BASE_DIR, "data", "sample_id_cards")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# =========================================================
# --- Advanced CSS Injection for Futuristic HUD Theme ---
# =========================================================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');

    /* --- Core Page Overrides --- */
    .stApp {{
        background: radial-gradient(circle, #10192a 0%, #060912 100%);
        color: #e0f2fe;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
    }}
    
    /* Permanent Scanline Overlay Effect */
    .stApp::before {{
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        background-size: 100% 4px, 3px 100%;
        z-idex: 2;
        pointer-events: none;
        opacity: 0.3;
    }}

    /* --- Glowing Sidebar --- */
    [data-testid="stSidebar"] {{
        background-color: #04060b;
        border-right: 2px solid #00f2fe;
        box-shadow: 5px 0px 15px rgba(0, 242, 254, 0.2);
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: #00f2fe;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px #00f2fe;
    }}

    /* --- HUD Styling for Content Panels (Glassmorphism + Neon) --- */
    [data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {{
        background: rgba(16, 25, 42, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
    }}

    /* --- Status Highlighting --- */
    .stAlert {{
        background-color: rgba(6, 9, 18, 0.8) !important;
        border-radius: 5px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }}
    /* Access Granted (Green Luminous) */
    .stAlert[data-baseweb="notification"] > div:first-child {{
        border: 2px solid #0f0;
        box-shadow: 0 0 10px #0f0;
        color: #0f0;
        background-color: rgba(0, 50, 0, 0.5);
    }}
    /* Access Denied (Red Luminous) */
    .stAlert[data-baseweb="notification"][class*="st-emotion-cache"] > div:first-child {{
        border: 2px solid #f00;
        box-shadow: 0 0 10px #f00;
        color: #f00;
        background-color: rgba(50, 0, 0, 0.5);
    }}

    /* --- Futurisitc Buttons --- */
    .stButton > button {{
        background: transparent !important;
        color: #00f2fe !important;
        border: 2px solid #00f2fe !important;
        border-radius: 5px !important;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 0 5px rgba(0, 242, 254, 0.5);
    }}
    .stButton > button:hover {{
        background: #00f2fe !important;
        color: #060912 !important;
        box-shadow: 0 0 20px #00f2fe;
    }}

    /* --- Header Title (Holographic Glitch Effect) --- */
    .hologram-title {{
        color: #fff;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 4px;
        position: relative;
        text-shadow: 0 0 10px #fff, 0 0 20px #00f2fe, 0 0 30px #00f2fe;
        animation: glitch 3s infinite;
    }}
    .sub-title {{
        color: #00f2fe;
        text-align: center;
        font-size: 1rem;
        margin-top: -10px;
        margin-bottom: 30px;
        opacity: 0.8;
    }}

    @keyframes glitch {{
        0% {{ text-shadow: 0 0 10px #fff, 0 0 20px #00f2fe; }}
        2% {{ text-shadow: 2px 0 red, -2px 0 blue; }}
        4% {{ text-shadow: 0 0 10px #fff, 0 0 20px #00f2fe; }}
        98% {{ text-shadow: 0 0 10px #fff, 0 0 20px #00f2fe; }}
        100% {{ text-shadow: -2px 0 red, 2px 0 blue; }}
    }}
    </style>
""", unsafe_allow_html=True)

# Audio Text-to-Speech Helper (Retained for accessibility)
def speak_alert(text):
    clean_text = text.replace("'", "").replace('"', '')
    js_code = f"""
        <script>
            var msg = new SpeechSynthesisUtterance('{clean_text}');
            msg.rate = 0.9; // Slightly slower, more bureaucratic voice
            window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(js_code, height=0)

# =========================================================
# --- Main Interface Content (HUD Panels) ---
# =========================================================

# --- Header Banner ---
st.markdown('<div class="hologram-title">SENTINEL // GATE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">CHRIST // UNIVERSITY — COMPLIANCE MONITOR v3.1</div>', unsafe_allow_html=True)

# --- Session State Initialization ---
if "engine" not in st.session_state:
    with st.spinner("INITIATING CORE AI // OCR // DATABASE SYNC..."):
        st.session_state.engine = ComplianceEngine()

if "audit_log" not in st.session_state:
    st.session_state.audit_log = [
        {"Time": "08:30:12", "Gate": "Gamma-1", "Reg No": "2582401", "Status": "COMPLIANT", "Reason": "System.ID.Valid"},
        {"Time": "08:35:45", "Gate": "Gamma-1", "Reg No": "2582402", "Status": "NON-COMPLIANT", "Reason": "Error.ID.BadgeMissing"},
        {"Time": "08:42:01", "Gate": "Gamma-1", "Reg No": "2582405", "Status": "COMPLIANT", "Reason": "System.ID.Valid"},
    ]

engine = st.session_state.engine

# --- Top Real-Time HUD Metrics ---
with st.container():
    m1, m2, m3, m4 = st.columns(4)
    total_scans = len(st.session_state.audit_log)
    non_compliant_count = sum(1 for log in st.session_state.audit_log if log["Status"] == "NON-COMPLIANT")

    with m1: st.metric(label="📍 ACTIVE NODE", value="Gamma Gate - A")
    with m2: st.metric(label="📊 TOTAL CYCLES", value=total_scans)
    with m3: st.metric(label="⚠️ VIO FLAGS", value=non_compliant_count)
    with m4: st.metric(label="🌐 UPLINK STATUS", value="SECURE")

st.divider()

# --- Sidebar Controls ---
st.sidebar.title("SECURITY PROTOCOLS")

input_mode = st.sidebar.radio(
    "Select Input Matrix",
    ["🔴 Live Neural Feed", "📁 Static Data Stream"]
)

campus_gate = st.sidebar.selectbox(
    "Active Node Location",
    ["Pedestrian Node Gamma-1", "Vehicular Node Beta-2", "Library Databank", "Hostel Grid Alpha"]
)

enable_audio = st.sidebar.checkbox("🔊 Enable Vocoder Feedback", value=True)

# --- Main Content Area (Scanner Panel) ---
col1, col2 = st.columns([1.2, 1])

image_to_process = None

with col1:
    with st.container():
        st.subheader("📷 NEURAL STREAM // GAMMA-1")

        if input_mode == "🔴 Live Neural Feed":
            st.caption("Awaiting Student Identification Matrix...")
            run_feed = st.checkbox("Turn On Webcam", value=False)
            camera_placeholder = st.empty()
            
            if run_feed:
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) # Force HD capture
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                
                scan_now = st.button("📸 CAPTURE MATRIX", type="primary", use_container_width=True)
                
                while cap.isOpened() and run_feed and not scan_now:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # HUD overlay simulated (simple border)
                    cv2.rectangle(frame_rgb, (10,10), (1270, 710), (254, 242, 0), 2) # Cyan border

                    camera_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                    time.sleep(0.01)

                if scan_now and cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        temp_filename = os.path.join(OUTPUTS_DIR, f"cap_{uuid.uuid4().hex[:6]}.jpg")
                        cv2.imwrite(temp_filename, frame)
                        image_to_process = temp_filename

        else: # Upload / Sample Mode
            st.caption("Upload static identification data stream.")
            sample_files = sorted(glob.glob(os.path.join(SAMPLE_CARDS_DIR, "*.png")))
            choice = st.selectbox("Select Sample ID Card", sample_files, format_func=lambda p: os.path.basename(p)) if sample_files else None
            uploaded = st.file_uploader("Or Upload Static Image", type=["png", "jpg", "jpeg"])

            if uploaded is not None:
                tmp_path = os.path.join(OUTPUTS_DIR, f"{uuid.uuid4().hex[:6]}_{uploaded.name}")
                with open(tmp_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                image_to_process = tmp_path
            elif choice:
                image_to_process = choice

            if image_to_process:
                # Add cyan glow to image display
                st.markdown(
                    f'<div style="border: 2px solid #00f2fe; box-shadow: 0 0 15px rgba(0, 242, 254, 0.5); border-radius: 5px; overflow: hidden;">',
                    unsafe_allow_html=True
                )
                st.image(image_to_process, caption="Data Stream Source", use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                trigger_scan = st.button("▶ PROCESS CYCLE", type="primary", use_container_width=True)

with col2:
    with st.container():
        st.subheader("🔍 NEURAL ANALYSIS RESULT")

        should_process = (input_mode == "🔴 Live Neural Feed" and image_to_process is not None) or \
                         (input_mode != "🔴 Live Neural Feed" and 'trigger_scan' in locals() and trigger_scan)

        if should_process and image_to_process:
            with st.spinner("CYBERNETIC_ANALYSIS_IN_PROGRESS..."):
                result = engine.process_frame(image_to_process)

            now_str = datetime.datetime.now().strftime("%H:%M:%S")

            if result.get("compliant", False):
                st.success(f"### ACCESS_GRANTED // Node:{campus_gate}")
                st.markdown(f"""
                ---
                > Student.ID: `{result.get('name', 'N/A')}`  
                > Registry.No: `{result.get('reg_no', 'N/A')}`  
                > Sector.Dept: `{result.get('department', 'N/A')}`  
                > Time.Cycle: `{now_str}`  
                """)

                if enable_audio:
                    speak_alert(f"Cycle Complete. Student {result.get('name', 'Student')} Identified. Access Granted.")

                st.session_state.audit_log.insert(0, {
                    "Time": now_str,
                    "Gate": campus_gate,
                    "Reg No": result.get('reg_no', 'N/A'),
                    "Status": "COMPLIANT",
                    "Reason": "Valid Identification"
                })

            else:
                st.error(f"### ACCESS_DENIED // Node:{campus_gate}")
                st.markdown(f"**Violation Detected:** Sector Rule Alpha-3: ID Card Missing/Invalid.")
                st.markdown(f"**Registry ID:** `{result.get('reg_no', 'System.Unknown')}`")

                if enable_audio:
                    speak_alert("Error. Access Denied. Sector Violation Detected.")

                st.session_state.audit_log.insert(0, {
                    "Time": now_str,
                    "Gate": campus_gate,
                    "Reg No": result.get('reg_no', 'Unknown'),
                    "Status": "NON-COMPLIANT",
                    "Reason": result.get('reason', 'ID Card Error')
                })

                with st.expander("📝 AI PROTOCOL REPORT", expanded=True):
                    st.info(result.get("report_text", "No cyber-report generated."))

        else:
            st.info("👈 Activate Neural Feed and click **CAPTURE MATRIX** (or stream data) to process identification cycle.")

# --- Cycle Log (Analytics HUD Panel) ---
st.divider()
with st.container():
    st.subheader("📋 SECURE NODE // LOG HISTORY")
    df = pd.DataFrame(st.session_state.audit_log)
    
    # Simple dark theme data display
    st.dataframe(df, use_container_width=True)

st.divider()
st.caption("🔒 **CHRIST SENTINEL** | Internal Campus Neural Monitoring v3.1 | Gamma Node")
