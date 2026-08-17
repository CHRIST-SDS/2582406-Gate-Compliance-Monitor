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

# --- EXPANDED ENROLLMENT DATABASE ---
MOCK_STUDENT_DB = {
    "2347101": {
        "name": "Nitheesh V",
        "department": "Data Science & Analytics",
        "enrollment_status": "Active Student"
    },
    "2347102": {
        "name": "Ananya Sharma",
        "department": "Computer Science",
        "enrollment_status": "Active Student"
    },
    "2347103": {
        "name": "Rohan Verma",
        "department": "Commerce & Management",
        "enrollment_status": "Suspended"
    },
    "2347104": {
        "name": "Kavya Nair",
        "department": "School of Law",
        "enrollment_status": "Active Student"
    },
    "2347105": {
        "name": "Rahul Menon",
        "department": "Psychology & Social Work",
        "enrollment_status": "Inactive / Graduated"
    },
    "2347106": {
        "name": "Priyanka Das",
        "department": "Economics & Finance",
        "enrollment_status": "Active Student"
    },
    "2347107": {
        "name": "Arjan Singh",
        "department": "Mechanical Engineering",
        "enrollment_status": "Suspended"
    },
    "2347108": {
        "name": "Sneha Hegde",
        "department": "Media Studies",
        "enrollment_status": "Active Student"
    },
    "2347109": {
        "name": "Vikramaditya Rao",
        "department": "Business Administration",
        "enrollment_status": "Active Student"
    },
    "2347110": {
        "name": "Fatima Khan",
        "department": "Data Science & Analytics",
        "enrollment_status": "Active Student"
    }
}

def verify_gate_compliance(frame, mock_reg_no):
    """
    Verifies if student is wearing/presenting an ID card and validates
    their current enrollment status in the university database.
    """
    card_detected = True  # Mock ID card detection flag
    
    if card_detected:
        student_info = MOCK_STUDENT_DB.get(mock_reg_no)
        if student_info and student_info["enrollment_status"] == "Active Student":
            return {
                "compliant": True,
                "reg_no": mock_reg_no,
                "student_record": student_info
            }
        else:
            status_reason = student_info["enrollment_status"] if student_info else "Record Not Found"
            return {
                "compliant": False,
                "reg_no": mock_reg_no,
                "reason": f"Non-Active Student ({status_reason})",
                "student_record": student_info if student_info else {}
            }
    else:
        return {
            "compliant": False,
            "reg_no": "Unknown",
            "reason": "ID Card Not Detected / Student Not Wearing ID"
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
    st.title("Gate Compliance & ID Verification Monitor")
    st.caption("Automated ID card detection and real-time university enrollment status verification.")

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
            <b>1. Visual Capture</b><br>
            <span style="color:#64748b;">Ingests feed via webcam snapshot or video stream.</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="step-box">
            <b>2. ID Card Detection</b><br>
            <span style="color:#64748b;">Scans frame to verify if the student is wearing/presenting an ID.</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="step-box">
            <b>3. Enrollment Lookup</b><br>
            <span style="color:#64748b;">Checks student ID against database to confirm current enrollment.</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="step-box">
            <b>4. Gate Decision</b><br>
            <span style="color:#64748b;">Grants campus access or flags non-compliant individuals.</span>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# --- DYNAMIC IN-PLACE METRICS CONTAINER ---
metrics_placeholder = st.empty()

def render_metrics(scanned, compliant, flagged):
    with metrics_placeholder.container():
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Scanned", scanned, help="Total frames or snapshots processed")
        m2.metric("Compliant Access", compliant, help="Verified active students wearing ID card")
        m3.metric("Flagged Violations", flagged, help="Missing ID cards or inactive enrollment records")

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
        selected_student = st.selectbox(
            "Select Student Profile for Camera Scan Simulation:",
            options=list(MOCK_STUDENT_DB.keys()),
            format_func=lambda x: f"{x} - {MOCK_STUDENT_DB[x]['name']} ({MOCK_STUDENT_DB[x]['department']})"
        )
        img_file_buffer = st.camera_input("Position student ID card toward camera")

    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        result = verify_gate_compliance(cv_img, mock_reg_no=selected_student)
        reg_no = result.get("reg_no", "Unknown")
        is_compliant = result.get("compliant", False)
        student_data = result.get("student_record", {})

        st.session_state.audit_logs.append({
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Scan Mode": "Webcam",
            "Registration No": reg_no,
            "Student Name": student_data.get("name", "N/A"),
            "Department": student_data.get("department", "N/A"),
            "Enrollment Status": student_data.get("enrollment_status", "N/A"),
            "Status": "COMPLIANT / GRANTED" if is_compliant else "FLAGGED / DENIED",
            "Violation Reason": "None" if is_compliant else result.get("reason", "Unknown")
        })

        if is_compliant:
            status_card.success(f"ACCESS GRANTED | Reg No: **{reg_no}**")
            details_card.json({
                "Student Name": student_data.get("name", "N/A"),
                "Department": student_data.get("department", "N/A"),
                "Enrollment Status": student_data.get("enrollment_status", "N/A"),
                "ID Card Detected": "Yes",
                "Campus Entry": "Authorized"
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
        db_keys = list(MOCK_STUDENT_DB.keys())

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1
            if frame_idx % frame_rate_skip != 0:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

            simulated_reg_no = db_keys[(len(st.session_state.audit_logs)) % len(db_keys)]
            result = verify_gate_compliance(frame, mock_reg_no=simulated_reg_no)
            
            reg_no = result.get("reg_no", "Unknown")
            is_compliant = result.get("compliant", False)
            student_data = result.get("student_record", {})

            st.session_state.audit_logs.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Scan Mode": "Video Stream",
                "Registration No": reg_no,
                "Student Name": student_data.get("name", "N/A"),
                "Department": student_data.get("department", "N/A"),
                "Enrollment Status": student_data.get("enrollment_status", "N/A"),
                "Status": "COMPLIANT / GRANTED" if is_compliant else "FLAGGED / DENIED",
                "Violation Reason": "None" if is_compliant else result.get("reason", "Unknown")
            })

            if is_compliant:
                status_card.success(f"ACCESS GRANTED | Reg No: **{reg_no}**")
                details_card.json({
                    "Student Name": student_data.get("name", "N/A"),
                    "Department": student_data.get("department", "N/A"),
                    "Enrollment Status": student_data.get("enrollment_status", "N/A"),
                    "ID Card Detected": "Yes",
                    "Campus Entry": "Authorized"
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
