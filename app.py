import os
import time
import tempfile
import cv2
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Gate Compliance Monitor | Christ University",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_PATH = "christ_logo.png"

# --- INITIALIZE SESSION LOGS ---
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

# --- CUSTOM ACADEMIC PORTAL STYLING ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
    }
    .portal-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .step-box {
        background-color: #f1f5f9;
        border-left: 4px solid #1e3a8a;
        padding: 10px 14px;
        border-radius: 4px;
        margin: 5px 0;
        font-size: 0.88rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- MOCK STUDENT DATABASE ---
MOCK_STUDENT_DB = {
    "2347101": {
        "name": "Nitheesh V",
        "department": "Data Science & Analytics",
        "card_status": "Active",
        "books_issued": 2,
        "pending_dues": 0
    },
    "2347102": {
        "name": "Ananya Sharma",
        "department": "Computer Science",
        "card_status": "Active",
        "books_issued": 1,
        "pending_dues": 150
    },
    "2347103": {
        "name": "Rohan Verma",
        "department": "Commerce & Management",
        "card_status": "Suspended",
        "books_issued": 0,
        "pending_dues": 500
    }
}

def verify_gate_compliance(frame, mock_reg_no="2347101"):
    card_detected = True  # Mock card presence flag
    
    if card_detected:
        student_info = MOCK_STUDENT_DB.get(mock_reg_no)
        if student_info and student_info["card_status"] == "Active":
            return {
                "compliant": True,
                "reg_no": mock_reg_no,
                "library_record": student_info
            }
        else:
            return {
                "compliant": False,
                "reg_no": mock_reg_no,
                "reason": "Inactive or Suspended Student Account",
                "library_record": student_info
            }
    else:
        return {
            "compliant": False,
            "reg_no": "Unknown",
            "reason": "ID Card Not Detected / Unreadable"
        }

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_column_width=True)
    else:
        st.warning("christ_logo.png missing from root directory.")
    
    st.markdown("### Surveillance Control")
    mode = st.radio(
        "Scan Mode:",
        ["Live Camera Snapshot", "Video Feed Upload"],
        help="Choose between webcam snapshot inspection or offline surveillance video analysis."
    )
    
    st.divider()
    
    # --- AUDIT LOG DOWNLOAD BUTTON ---
    st.markdown("### Export Audit Data")
    if st.session_state.audit_logs:
        df_logs = pd.DataFrame(st.session_state.audit_logs)
        csv_data = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Audit Log (CSV)",
            data=csv_data,
            file_name=f"gate_audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.caption("No scan records generated yet.")

    st.divider()
    st.info("Demo Mode Active: Bounding box detection runs on mock mode. Swap card_detected with best.pt YOLOv8 weights for live model inference.")

# --- MAIN HEADER ---
col_head1, col_head2 = st.columns([4, 1.5])
with col_head1:
    st.title("Gate Compliance & Library Access Monitor")
    st.caption("Automated visual ID verification, surveillance compliance auditing, and real-time library database synchronization.")

with col_head2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_column_width=True)

# --- SYSTEM WORKFLOW GUIDE ---
with st.expander("System Overview & Workflow Guide", expanded=False):
    st.markdown("The automated gate surveillance engine operates in four steps:")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="step-box">
            <b>1. Frame Capture</b><br>
            <span style="color:#64748b;">Ingests visual input via webcam snapshot or video stream.</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="step-box">
            <b>2. ID Detection</b><br>
            <span style="color:#64748b;">Identifies student ID card presence within the frame.</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="step-box">
            <b>3. Database Verification</b><br>
            <span style="color:#64748b;">Cross-checks registration ID with active student records.</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="step-box">
            <b>4. Access Decision</b><br>
            <span style="color:#64748b;">Grants campus entry or flags compliance non-adherence.</span>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# --- DYNAMIC IN-PLACE METRICS CONTAINER ---
metrics_placeholder = st.empty()

def render_metrics(scanned, compliant, flagged):
    with metrics_placeholder.container():
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Scanned", scanned, help="Total frames or snapshots processed")
        m2.metric("Compliant Access", compliant, help="Verified active students granted entry")
        m3.metric("Flagged Violations", flagged, help="Unrecognized or suspended accounts blocked")

total_scanned = len(st.session_state.audit_logs)
compliant_count = sum(1 for log in st.session_state.audit_logs if log["Status"] == "COMPLIANT / GRANTED")
flagged_count = sum(1 for log in st.session_state.audit_logs if log["Status"] == "FLAGGED / DENIED")

render_metrics(total_scanned, compliant_count, flagged_count)

col_stream, col_status = st.columns([3.2, 2])

with col_status:
    st.subheader("Real-Time Access Audit")
    status_card = st.empty()
    details_card = st.empty()

# --- MODE 1: LIVE CAMERA SNAPSHOT ---
if mode == "Live Camera Snapshot":
    with col_stream:
        st.subheader("Webcam Inspection Station")
        img_file_buffer = st.camera_input("Position student ID card toward camera")

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        result = verify_gate_compliance(cv_img, mock_reg_no="2347101")
        reg_no = result.get("reg_no", "Unknown")
        is_compliant = result.get("compliant", False)
        lib_data = result.get("library_record", {})

        st.session_state.audit_logs.append({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Scan Mode": "Webcam",
            "Registration No": reg_no,
            "Student Name": lib_data.get("name", "N/A"),
            "Department": lib_data.get("department", "N/A"),
            "Status": "COMPLIANT / GRANTED" if is_compliant else "FLAGGED / DENIED",
            "Violation Reason": "None" if is_compliant else result.get("reason", "Unknown")
        })

        if is_compliant:
            status_card.success(f"ACCESS GRANTED | Reg No: **{reg_no}**")
            details_card.json({
                "Student Name": lib_data.get("name", "N/A"),
                "Department": lib_data.get("department", "N/A"),
                "Library Card Status": lib_data.get("card_status", "Active"),
                "Books Issued": lib_data.get("books_issued", 0),
                "Pending Dues": f"₹{lib_data.get('pending_dues', 0)}"
            })
        else:
            status_card.error(f"ACCESS DENIED | Reg No: **{reg_no}**")
            details_card.warning(f"**Violation Reason:** {result.get('reason', 'ID Card Not Found / Inactive Account')}")

        total_scanned = len(st.session_state.audit_logs)
        compliant_count = sum(1 for log in st.session_state.audit_logs if log["Status"] == "COMPLIANT / GRANTED")
        flagged_count = sum(1 for log in st.session_state.audit_logs if log["Status"] == "FLAGGED / DENIED")
        render_metrics(total_scanned, compliant_count, flagged_count)

# --- MODE 2: VIDEO FEED UPLOAD ---
else:
    with col_stream:
        st.subheader("CCTV Video Stream Audit")
        uploaded_video = st.file_uploader("Upload gate surveillance video (.mp4, .avi, .mov)", type=["mp4", "avi", "mov"])
        start_scan = st.button("Start Video Scan", type="primary")
        frame_placeholder = st.empty()

    if uploaded_video is not None and start_scan:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_video.read())
        tfile.close()
        video_path = tfile.name

        cap = cv2.VideoCapture(video_path)
        frame_rate_skip = 30
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1
            if frame_idx % frame_rate_skip != 0:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

            mock_id = "2347101" if (len(st.session_state.audit_logs) + 1) % 2 != 0 else "2347103"
            result = verify_gate_compliance(frame, mock_reg_no=mock_id)
            
            reg_no = result.get("reg_no", "Unknown")
            is_compliant = result.get("compliant", False)
            lib_data = result.get("library_record", {})

            st.session_state.audit_logs.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Scan Mode": "Video Stream",
                "Registration No": reg_no,
                "Student Name": lib_data.get("name", "N/A"),
                "Department": lib_data.get("department", "N/A"),
                "Status": "COMPLIANT / GRANTED" if is_compliant else "FLAGGED / DENIED",
                "Violation Reason": "None" if is_compliant else result.get("reason", "Unknown")
            })

            if is_compliant:
                status_card.success(f"ACCESS GRANTED | Reg No: **{reg_no}**")
                details_card.json({
                    "Student Name": lib_data.get("name", "N/A"),
                    "Department": lib_data.get("department", "N/A"),
                    "Library Card Status": lib_data.get("card_status", "Active"),
                    "Books Issued": lib_data.get("books_issued", 0),
                    "Pending Dues": f"₹{lib_data.get('pending_dues', 0)}"
                })
            else:
                status_card.error(f"ACCESS DENIED | Reg No: **{reg_no}**")
                details_card.warning(f"**Violation Reason:** {result.get('reason', 'ID Card Not Found / Inactive Account')}")

            total_scanned = len(st.session_state.audit_logs)
            compliant_count = sum(1 for log in st.session_state.audit_logs if log["Status"] == "COMPLIANT / GRANTED")
            flagged_count = sum(1 for log in st.session_state.audit_logs if log["Status"] == "FLAGGED / DENIED")
            render_metrics(total_scanned, compliant_count, flagged_count)

            time.sleep(1.0)

        cap.release()
        
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
        except Exception:
            pass

    else:
        frame_placeholder.info("Upload a surveillance video file above and click **Start Video Scan** to begin live analysis.")
