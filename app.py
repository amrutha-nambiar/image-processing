import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io

# --- Streamlit Page Config ---
st.set_page_config(page_title="Filterly", layout="wide")

# --- Snapchat-inspired Style ---
st.markdown("""
    <style>
        /* Fullscreen clean background */
        [data-testid="stAppViewContainer"] {
            background-color: black;
            color: white;
        }

        /* Hide Streamlit's default header & footer */
        header, footer, [data-testid="stToolbar"] {visibility: hidden !important;}

        /* Center main content */
        [data-testid="stVerticalBlock"] {
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        /* App title */
        h1 {
            color: #FFFC00 !important;
            font-size: 2.8em !important;
            margin-bottom: 10px;
            font-weight: 700;
        }

        /* Floating control box (filters & sliders) */
        .control-panel {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 252, 0, 0.15);
            border: 2px solid rgba(255, 252, 0, 0.6);
            border-radius: 20px;
            padding: 15px 25px;
            backdrop-filter: blur(12px);
            color: white;
            width: 80%;
            max-width: 600px;
        }

        /* Labels */
        label, .stSelectbox label, .stSlider label {
            color: white !important;
            font-weight: 500;
        }

        /* Buttons (Snapchat-style) */
        div.stButton > button {
            background-color: #FFFC00 !important;
            color: black !important;
            border: none;
            border-radius: 50%;
            width: 80px;
            height: 80px;
            font-size: 1.5em;
            font-weight: 700;
            box-shadow: 0 0 15px rgba(255, 252, 0, 0.7);
        }

        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(255, 252, 0, 1);
        }

        /* Download button */
        .download-btn > button {
            background-color: #FFFC00 !important;
            color: black !important;
            font-weight: 600;
            border-radius: 12px;
            padding: 0.5rem 1.2rem;
            border: none;
        }

        .download-btn > button:hover {
            background-color: #FFF56A !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1>📸 Filterly</h1>", unsafe_allow_html=True)

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

# --- Filter Controls (Floating Box) ---
st.markdown('<div class="control-panel">', unsafe_allow_html=True)
filter_name = st.selectbox(
    "Filter",
    ["none", "grayscale", "sepia", "invert", "blur", "sharpen", "edge", "emboss", "contour"]
)
brightness = st.slider("Brightness", 0, 200, 100)
contrast = st.slider("Contrast", 0, 200, 100)
intensity = st.slider("Intensity", 1, 10, 2)
st.markdown('</div>', unsafe_allow_html=True)

# --- Filter Logic ---
def apply_filter(frame, filter_name, brightness=100, contrast=100, intensity=2):
    frame = np.array(frame)
    pil_img = Image.fromarray(frame)

    # Brightness & contrast
    pil_img = ImageEnhance.Brightness(pil_img).enhance(brightness / 100)
    pil_img = ImageEnhance.Contrast(pil_img).enhance(contrast / 100)
    frame = np.array(pil_img)

    # Apply filters
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

# --- Display ---
if image is not None:
    filtered_image = apply_filter(image, filter_name, brightness, contrast, intensity)
    st.image(filtered_image, use_container_width=True)

    buf = io.BytesIO()
    filtered_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.markdown('<div class="download-btn">', unsafe_allow_html=True)
    st.download_button(
        label="💾 Save",
        data=byte_im,
        file_name="filtered_snap.png",
        mime="image/png"
    )
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("📸 Take or upload a photo to apply filters.")
