import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import time

# --- Streamlit Page Config ---
st.set_page_config(page_title="📸 Web Camera Filters", layout="centered")

st.title("📸 Camera Filters with Sliders")

# --- Session state setup ---
if "snapshot" not in st.session_state:
    st.session_state.snapshot = None
if "camera_running" not in st.session_state:
    st.session_state.camera_running = False
if "take_snapshot" not in st.session_state:
    st.session_state.take_snapshot = False

# --- Sidebar controls ---
st.sidebar.header("🎨 Filters & Adjustments")
filter_name = st.sidebar.selectbox(
    "Choose a filter:",
    ["none", "grayscale", "sepia", "invert", "blur"]
)

brightness = st.sidebar.slider("Brightness", 0, 200, 100)
contrast = st.sidebar.slider("Contrast", 0, 200, 100)

# --- Helper function for filters ---
def apply_filter(frame, filter_name, brightness=100, contrast=100):
    frame = cv2.convertScaleAbs(frame, alpha=contrast / 100, beta=brightness - 100)
    if filter_name == "grayscale":
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    elif filter_name == "sepia":
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        frame = cv2.transform(frame, kernel)
        frame = np.clip(frame, 0, 255)
    elif filter_name == "invert":
        frame = cv2.bitwise_not(frame)
    elif filter_name == "blur":
        frame = cv2.GaussianBlur(frame, (15, 15), 0)
    return frame

# --- Layout ---
frame_placeholder = st.empty()
snapshot_placeholder = st.empty()

col1, col2, col3, col4 = st.columns(4)
start = col1.button("▶ Start Camera")
stop = col2.button("⏹ Stop Camera")
capture = col3.button("📸 Take Snapshot")
download = col4.button("💾 Download Snapshot")

# --- Button handling logic ---
if start:
    st.session_state.camera_running = True
if stop:
    st.session_state.camera_running = False
if capture:
    st.session_state.take_snapshot = True

# --- Camera loop ---
if st.session_state.camera_running:
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("🚫 Unable to access webcam. Check permissions or device availability.")
        st.session_state.camera_running = False
    else:
        st.info("📷 Camera is active. Press '⏹ Stop Camera' to end.")

        # Keep showing frames until stopped
        while st.session_state.camera_running:
            ret, frame = cap.read()
            if not ret:
                st.error("⚠️ Cannot read from webcam.")
                break

            frame = cv2.flip(frame, 1)
            frame = apply_filter(frame, filter_name, brightness, contrast)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame_placeholder.image(frame_rgb, channels="RGB")

            # Handle snapshot capture
            if st.session_state.take_snapshot:
                st.session_state.snapshot = frame_rgb.copy()
                st.session_state.take_snapshot = False
                st.success("📸 Snapshot captured!")
                snapshot_placeholder.image(st.session_state.snapshot, caption="Snapshot")
                break  # Exit loop to show static snapshot

            time.sleep(0.05)

        cap.release()

# --- Download snapshot section ---
if st.session_state.snapshot is not None:
    if download:
        img = Image.fromarray(st.session_state.snapshot)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="⬇ Download Your Snapshot",
            data=byte_im,
            file_name="snapshot.png",
            mime="image/png"
        )
