import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io

st.set_page_config(page_title="Filterly", layout="wide")

# --- Modern minimal style ---
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #fff8e1, #fff3c0);
            color: #111;
            font-family: 'Poppins', sans-serif;
        }

        header, footer, [data-testid="stToolbar"] {visibility: hidden;}

        /* Title bar */
        .topbar {
            width: 100%;
            text-align: center;
            padding: 1rem 0;
            font-size: 2.2rem;
            font-weight: 700;
            color: #fbc02d;
            letter-spacing: 2px;
        }

        /* Two column layout */
        .main-layout {
            display: flex;
            justify-content: space-evenly;
            align-items: flex-start;
            margin-top: 2rem;
        }

        /* Image area */
        .image-panel {
            flex: 1;
            text-align: center;
            padding: 1rem;
        }

        /* Filter buttons */
        .filters-panel {
            flex: 0.3;
            background: rgba(255,255,255,0.6);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 1.5rem;
            margin-right: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        .filters-panel button {
            background: none;
            border: 2px solid #fbc02d;
            color: #111;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            margin: 0.3rem;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 600;
        }

        .filters-panel button:hover {
            background: #fbc02d;
            color: #fff;
        }

        /* Sliders container */
        .bottom-panel {
            position: fixed;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 15px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        }

        .download-btn > button {
            background-color: #fbc02d !important;
            color: black !important;
            font-weight: 600;
            border-radius: 12px;
            padding: 0.5rem 1.2rem;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title Bar ---
st.markdown("<div class='topbar'>📸 Filterly</div>", unsafe_allow_html=True)

# --- Tabs for Input ---
tab1, tab2 = st.tabs(["📷 Camera", "📁 Upload"])

image = None
with tab1:
    img_file_buffer = st.camera_input("")
    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)

with tab2:
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

# --- Filters List ---
filter_list = ["none", "grayscale", "sepia", "invert", "blur", "sharpen", "edge", "emboss", "contour"]
cols = st.columns(len(filter_list))

# --- Save selected filter ---
if "filter" not in st.session_state:
    st.session_state["filter"] = "none"

for i, f in enumerate(filter_list):
    if cols[i].button(f.capitalize()):
        st.session_state["filter"] = f

selected_filter = st.session_state["filter"]

# --- Filter Logic ---
def apply_filter(frame, filter_name, brightness=100, contrast=100, intensity=2):
    frame = np.array(frame)
    pil_img = Image.fromarray(frame)
    pil_img = ImageEnhance.Brightness(pil_img).enhance(brightness / 100)
    pil_img = ImageEnhance.Contrast(pil_img).enhance(contrast / 100)
    frame = np.array(pil_img)

    if filter_name == "grayscale":
        frame = np.dot(frame[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        frame = np.stack([frame] * 3, axis=-1)
    elif filter_name == "sepia":
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        frame = np.clip(frame.dot(kernel.T), 0, 255).astype(np.uint8)
    elif filter_name == "invert":
        frame = 255 - frame
    elif filter_name == "blur":
        frame = np.array(Image.fromarray(frame).filter(ImageFilter.GaussianBlur(intensity)))
    elif filter_name == "sharpen":
        for _ in range(intensity):
            frame = np.array(Image.fromarray(frame).filter(ImageFilter.SHARPEN))
    elif filter_name == "edge":
        frame = np.array(Image.fromarray(frame).filter(ImageFilter.FIND_EDGES))
    elif filter_name == "emboss":
        frame = np.array(Image.fromarray(frame).filter(ImageFilter.EMBOSS))
    elif filter_name == "contour":
        frame = np.array(Image.fromarray(frame).filter(ImageFilter.CONTOUR))
    return Image.fromarray(frame)

# --- Image Display ---
if image is not None:
    brightness = st.slider("Brightness", 0, 200, 100, key="bright")
    contrast = st.slider("Contrast", 0, 200, 100, key="cont")
    intensity = st.slider("Intensity", 1, 10, 2, key="intens")

    filtered_image = apply_filter(image, selected_filter, brightness, contrast, intensity)
    st.image(filtered_image, use_container_width=True)

    buf = io.BytesIO()
    filtered_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.markdown('<div class="download-btn">', unsafe_allow_html=True)
    st.download_button("💾 Save", byte_im, "filtered_snap.png", "image/png")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("📸 Take or upload a photo to apply filters.")
