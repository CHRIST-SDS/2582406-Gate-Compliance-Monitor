"""
Gate Compliance Monitor — Streamlit dashboard.

Run:  streamlit run app.py

First-time setup:
  python -m src.dummy_data_generator     # creates dummy library DB + sample cards
  ollama pull llama3                     # local LLM (optional, has fallback)
  # start AUTOMATIC1111 with --api       # local image gen (optional, has fallback)
"""
import os
import glob
import streamlit as st

from src.compliance_engine import ComplianceEngine

st.set_page_config(page_title="Gate Compliance Monitor", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CARDS_DIR = os.path.join(BASE_DIR, "data", "sample_id_cards")

st.title("🎓 AI-Powered Gate Compliance Monitor")
st.caption("Local LLM (Ollama) + Local Image Gen (Stable Diffusion) — fully offline, no cloud APIs")

if "engine" not in st.session_state:
    with st.spinner("Initializing detector, OCR, and DB sync..."):
        st.session_state.engine = ComplianceEngine()

engine = st.session_state.engine

st.sidebar.header("Simulate a gate scan")
sample_files = sorted(glob.glob(os.path.join(SAMPLE_CARDS_DIR, "*.png")))

if not sample_files:
    st.warning("No sample ID cards found. Run: `python -m src.dummy_data_generator`")
else:
    choice = st.sidebar.selectbox("Choose a sample card to scan", sample_files,
                                   format_func=lambda p: os.path.basename(p))
    uploaded = st.sidebar.file_uploader("...or upload your own card image", type=["png", "jpg", "jpeg"])

    scan_btn = st.sidebar.button("▶ Scan at Gate", type="primary")

    col1, col2 = st.columns([1, 1.4])

    image_path = choice
    if uploaded is not None:
        tmp_path = os.path.join(BASE_DIR, "outputs", uploaded.name)
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        image_path = tmp_path

    with col1:
        st.subheader("Gate camera frame")
        st.image(image_path, width=350)

    if scan_btn:
        with col2:
            with st.spinner("Detecting → OCR → DB lookup → (LLM + Image Gen if flagged)..."):
                result = engine.process_frame(image_path)

            if result["compliant"]:
                st.success(f"✅ COMPLIANT — {result['name']} ({result['reg_no']}), "
                           f"{result['department']}")
                st.json(result)
            else:
                st.error(f"🚫 NON-COMPLIANT — {result['reg_no']}")
                st.write(f"**Reason:** {result['reason']}")
                st.markdown("**LLM-generated incident report:**")
                st.info(result["report_text"])
                st.markdown("**AI-generated alert visual:**")
                st.image(result["alert_image_path"], width=300)

st.divider()
st.caption("Repository structure follows course guidelines — see README.md for setup, "
           "architecture, and demo instructions.")
