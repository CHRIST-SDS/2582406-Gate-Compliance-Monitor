"""
Christ University — Gate Compliance & Access Monitor
Streamlit Dashboard for Campus Security & Administration

Run:
    streamlit run app.py

First-time setup:
    python -m src.dummy_data_generator     # creates dummy database + sample cards
    ollama pull llama3                     # local LLM (optional, has fallback)
"""

import os
import glob
import uuid
import datetime
import pandas as pd
import streamlit as st

from src.compliance_engine import ComplianceEngine

# --- Page Setup & Campus Branding ---
st.set_page_config(
    page_title="Christ University — Gate Compliance Monitor",
    page_icon="🎓",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CARDS_DIR = os.path.join(BASE_DIR, "data", "sample_id_cards")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Custom Styling for College Theme
st.markdown("""
    <style>
    .main-header {
        background-color: #0d233a;
        padding: 1.2rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: #ffffff; margin: 0; font-size: 2rem; }
    .main-header p { color: #d0e1f9; margin: 0; font-size: 0.95rem; }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0d233a;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Banner ---
st.markdown("""
    <div class="main-header">
        <h1>🎓 CHRIST (Deemed to be University)</h1>
        <p>Smart Security & Automated Gate Compliance System | Campus Access Control</p>
    </div>
""", unsafe_allow_html=True)

# --- Initialize Engine ---
if "engine" not in st.session_state:
    with st.spinner("Initializing campus detector models, OCR engine, and student DB..."):
        st.session_state.engine = ComplianceEngine()

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

engine = st.session_state.engine

# --- Top Metric Dashboard ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="📍 Gate Location", value="Main Gate - Entry A")
with m2:
    st.metric(label="📊 Scans Today", value=len(st.session_state.audit_log) + 142)
with m3:
    st.metric(label="⚠️ Non-Compliance Flags", value=3, delta="+1 this hour", delta_color="inverse")
with m4:
    st.metric(label="🟢 System Status", value="Active / Offline AI")

st.divider()

# --- Sidebar Controls ---
st.sidebar.image("https://img.icons8.com/color/96/university.png", width=70)
st.sidebar.title("Campus Security Controls")

campus_gate = st.sidebar.selectbox(
    "Select Active Gate",
    ["Main Gate 1 (Pedestrian)", "Gate 2 (Vehicular)", "Library Entrance", "Hostel Block 1"]
)

compliance_mode = st.sidebar.multiselect(
    "Active Enforcement Checks",
    ["Student ID Card Verification", "Library Clearance", "Dress Code Compliance", "Vehicle Pass Check"],
    default=["Student ID Card Verification", "Library Clearance"]
)

st.sidebar.subheader("Simulate Gate Camera Scan")
sample_files = sorted(glob.glob(os.path.join(SAMPLE_CARDS_DIR, "*.png")))

if not sample_files:
    st.sidebar.error("No sample ID cards found. Run: `python -m src.dummy_data_generator`")
else:
    choice = st.sidebar.selectbox(
        "Select Test Sample ID",
        sample_files,
        format_func=lambda p: os.path.basename(p)
    )
    uploaded = st.sidebar.file_uploader("...or Upload Scan Capture", type=["png", "jpg", "jpeg"])

    scan_btn = st.sidebar.button("▶ Trigger Gate Scan", type="primary", use_container_width=True)

    # --- Main Content Area ---
    col1, col2 = st.columns([1, 1.3])

    # Determine Image Path
    image_path = choice
    if uploaded is not None:
        file_ext = os.path.splitext(uploaded.name)[1]
        unique_name = f"{uuid.uuid4().hex[:8]}_{uploaded.name}"
        tmp_path = os.path.join(OUTPUTS_DIR, unique_name)
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        image_path = tmp_path

    with col1:
        st.subheader("📷 Live Camera Stream")
        st.image(image_path, caption=f"Source: {campus_gate}", use_column_width=True)

    with col2:
        st.subheader("🔍 Compliance & Identity Verification")

        if scan_btn:
            with st.spinner("Processing OCR → Querying Student Database → Generating AI Incident Audit..."):
                result = engine.process_frame(image_path)

            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if result.get("compliant", False):
                st.success(f"### ✅ ACCESS GRANTED")
                st.markdown(f"""
                * **Student Name:** {result.get('name', 'N/A')}
                * **Register No:** `{result.get('reg_no', 'N/A')}`
                * **Department:** {result.get('department', 'N/A')}
                * **Timestamp:** `{now_str}`
                """)

                st.session_state.audit_log.insert(0, {
                    "Time": now_str,
                    "Gate": campus_gate,
                    "Reg No": result.get('reg_no', 'N/A'),
                    "Status": "COMPLIANT",
                    "Reason": "Valid Identification"
                })

                with st.expander("Show Raw Verification JSON"):
                    st.json(result)

            else:
                st.error(f"### 🚫 ACCESS DENIED — NON-COMPLIANT")
                st.markdown(f"**Register No / Target:** `{result.get('reg_no', 'Unknown')}`")
                st.markdown(f"**Flagged Reason:** {result.get('reason', 'Compliance Violation')}")

                st.session_state.audit_log.insert(0, {
                    "Time": now_str,
                    "Gate": campus_gate,
                    "Reg No": result.get('reg_no', 'N/A'),
                    "Status": "NON-COMPLIANT",
                    "Reason": result.get('reason', 'Compliance Violation')
                })

                # Tabs for AI Incident Details
                tab_report, tab_visual = st.tabs(["📝 AI Incident Report", "📸 Alert Visual"])

                with tab_report:
                    st.info(result.get("report_text", "No detailed report generated."))
                    st.button("📩 Escalate to Student Conduct Officer", key="notify_btn")

                with tab_visual:
                    if "alert_image_path" in result and os.path.exists(result["alert_image_path"]):
                        st.image(result["alert_image_path"], caption="AI-Generated Security Visual", width=320)
                    else:
                        st.warning("No visual alert generated.")
        else:
            st.info("👈 Select or upload a test card image and click **Trigger Gate Scan** to process entry.")

# --- Gate Audit History Table ---
st.divider()
st.subheader("📋 Today's Gate Log Summary")

if st.session_state.audit_log:
    df_log = pd.DataFrame(st.session_state.audit_log)
    st.dataframe(df_log, use_container_width=True)
else:
    st.caption("No scans recorded in current session. Perform a gate scan to see logs.")

st.caption("🔒 **CHRIST Security System** | Internal Campus Monitoring Dashboard")
