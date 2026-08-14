"""
Christ University — Smart Gate Compliance & Access Monitor
Streamlit Dashboard with Live Camera Feed & Accessibility Features

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

# --- Page Setup & Accessibility Config ---
st.set_page_config(
    page_title="Christ University — Gate Compliance Monitor",
    page_icon="🎓",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CARDS_DIR = os.path.join(BASE_DIR, "data", "sample_id_cards")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Custom Styling for Accessibility & College Theme
st.markdown("""
    <style>
    .main-header {
        background-color: #0d233a;
        padding: 1.2rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .main-header h1 { color: #ffffff; margin: 0; font-size: 2.2rem; }
    .main-header p { color: #d0e1f9; margin: 0; font-size: 1rem; }
    
    /* High-contrast status badges for accessibility */
    .status-granted {
        background-color: #1e7e34;
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    .status-denied {
        background-color: #bd2130;
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Audio Text-to-Speech Helper for Accessibility
def speak_alert(text):
    clean_text = text.replace("'", "").replace('"', '')
    js_code = f"""
        <script>
            var msg = new SpeechSynthesisUtterance('{clean_text}');
            window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(js_code, height=0)

# --- Header Banner ---
st.markdown("""
    <div class="main-header">
        <h1>🎓 CHRIST (Deemed to be University)</h1>
        <p>Smart Security & Automated Gate Compliance System | Live Feed & AI Monitor</p>
    </div>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "engine" not in st.session_state:
    with st.spinner("Initializing AI Models, OCR Engine, and Database..."):
        st.session_state.engine = ComplianceEngine()

if "audit_log" not in st.session_state:
    st.session_state.audit_log = [
        {"Time": "08:30:12", "Gate": "Main Gate 1", "Reg No": "2582401", "Status": "COMPLIANT", "Reason": "Valid ID"},
        {"Time": "08:35:45", "Gate": "Main Gate 1", "Reg No": "2582402", "Status": "NON-COMPLIANT", "Reason": "No ID Badge Detected"},
        {"Time": "08:42:01", "Gate": "Main Gate 1", "Reg No": "2582405", "Status": "COMPLIANT", "Reason": "Valid ID"},
    ]

engine = st.session_state.engine

# --- Top Real-Time Metrics ---
m1, m2, m3, m4 = st.columns(4)
total_scans = len(st.session_state.audit_log)
non_compliant_count = sum(1 for log in st.session_state.audit_log if log["Status"] == "NON-COMPLIANT")

with m1:
    st.metric(label="📍 Gate Location", value="Main Gate - Entry A")
with m2:
    st.metric(label="📊 Total Scans Today", value=total_scans)
with m3:
    st.metric(label="⚠️ Non-Compliance Flags", value=non_compliant_count, delta=f"{non_compliant_count} flags", delta_color="inverse")
with m4:
    st.metric(label="🔊 Audio Accessibility", value="Enabled")

st.divider()

# --- Sidebar Controls ---
st.sidebar.title("🎮 Gate Operations")

input_mode = st.sidebar.radio(
    "Select Camera Input Mode",
    ["🔴 Live Webcam Stream", "📁 Sample / Upload ID Card"]
)

campus_gate = st.sidebar.selectbox(
    "Active Gate Location",
    ["Main Gate 1 (Pedestrian)", "Gate 2 (Vehicular)", "Library Entrance", "Hostel Block 1"]
)

enable_audio = st.sidebar.checkbox("🔊 Enable Audio Voice Alerts", value=True)

# --- Main Content Area ---
tab_scan, tab_analytics = st.tabs(["🎥 Gate Scanner", "📈 Live Compliance Analytics"])

with tab_scan:
    col1, col2 = st.columns([1.2, 1])

    image_to_process = None

    with col1:
        st.subheader("📷 Camera Stream")

        if input_mode == "🔴 Live Webcam Stream":
            st.info("Point camera at student ID card or face.")
            run_feed = st.checkbox("Turn On Webcam", value=False)
            camera_placeholder = st.empty()
            
            if run_feed:
                cap = cv2.VideoCapture(0)
                scan_now = st.button("📸 Capture & Scan Frame", type="primary", use_container_width=True)
                
                while cap.isOpened() and run_feed and not scan_now:
                    ret, frame = cap.read()
                    if not ret:
                        st.error("Failed to access webcam.")
                        break
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    camera_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                    time.sleep(0.03)

                if scan_now and cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        temp_filename = os.path.join(OUTPUTS_DIR, f"webcam_{uuid.uuid4().hex[:6]}.jpg")
                        cv2.imwrite(temp_filename, frame)
                        image_to_process = temp_filename
                        st.success("Frame Captured Successfully!")

        else: # Sample / Upload Mode
            sample_files = sorted(glob.glob(os.path.join(SAMPLE_CARDS_DIR, "*.png")))
            choice = st.selectbox("Select Sample ID Card", sample_files, format_func=lambda p: os.path.basename(p)) if sample_files else None
            uploaded = st.file_uploader("Or Upload Image", type=["png", "jpg", "jpeg"])

            if uploaded is not None:
                tmp_path = os.path.join(OUTPUTS_DIR, f"{uuid.uuid4().hex[:6]}_{uploaded.name}")
                with open(tmp_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                image_to_process = tmp_path
            elif choice:
                image_to_process = choice

            if image_to_process:
                st.image(image_to_process, caption="Selected Image Source", use_column_width=True)
                trigger_scan = st.button("▶ Trigger Gate Scan", type="primary", use_container_width=True)

    with col2:
        st.subheader("🔍 Real-Time Compliance Results")

        should_process = (input_mode == "🔴 Live Webcam Stream" and image_to_process is not None) or \
                         (input_mode != "🔴 Live Webcam Stream" and 'trigger_scan' in locals() and trigger_scan)

        if should_process and image_to_process:
            with st.spinner("Processing OCR → Verifying Student ID → AI Incident Audit..."):
                result = engine.process_frame(image_to_process)

            now_str = datetime.datetime.now().strftime("%H:%M:%S")

            if result.get("compliant", False):
                st.markdown('<div class="status-granted">✅ ACCESS GRANTED</div>', unsafe_allow_html=True)
                st.markdown(f"""
                * **Student Name:** `{result.get('name', 'N/A')}`
                * **Register No:** `{result.get('reg_no', 'N/A')}`
                * **Department:** `{result.get('department', 'N/A')}`
                """)

                if enable_audio:
                    speak_alert(f"Access Granted. Welcome {result.get('name', 'Student')}")

                st.session_state.audit_log.insert(0, {
                    "Time": now_str,
                    "Gate": campus_gate,
                    "Reg No": result.get('reg_no', 'N/A'),
                    "Status": "COMPLIANT",
                    "Reason": "Valid Identification"
                })

            else:
                st.markdown('<div class="status-denied">🚫 ACCESS DENIED</div>', unsafe_allow_html=True)
                st.error(f"**Reason:** {result.get('reason', 'ID Card Not Detected / Invalid')}")

                if enable_audio:
                    speak_alert("Access Denied. Compliance Violation Detected.")

                st.session_state.audit_log.insert(0, {
                    "Time": now_str,
                    "Gate": campus_gate,
                    "Reg No": result.get('reg_no', 'Unknown'),
                    "Status": "NON-COMPLIANT",
                    "Reason": result.get('reason', 'Violation')
                })

                with st.expander("📝 AI Incident Report", expanded=True):
                    st.info(result.get("report_text", "No detailed report generated."))

        else:
            st.info("👈 Turn on camera and click **Capture & Scan Frame** (or select a file) to process compliance.")

# --- Analytics Tab ---
with tab_analytics:
    st.subheader("📊 Dynamic Gate Activity Insights")
    df = pd.DataFrame(st.session_state.audit_log)

    if not df.empty:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("### Compliance Ratio")
            fig_pie = px.pie(
                df, names="Status", title="Today's Gate Scans Breakdown",
                color="Status", color_discrete_map={"COMPLIANT": "#28a745", "NON-COMPLIANT": "#dc3545"}
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.markdown("### Recent Scans Log")
            st.dataframe(df, use_container_width=True, height=300)
    else:
        st.caption("No log data available yet.")

st.divider()
st.caption("🔒 **CHRIST Security System** | Gate Compliance & Accessibility Engine")
