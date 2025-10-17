import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io

# --- Streamlit Page Config ---
st.set_page_config(page_title="Filterly", layout="wide")

# --- Frosted Light Theme (Modern Style) ---
st.markdown("""
    <style>
        /* Soft frosted glass background */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(to bottom right, #f9fafc, #eef2f3);
            color: #222;
        }

        /* Hide default header/footer */
        header, footer, [data-testid="stToolbar"] {visibility: hidden !important;}

        /* Center main content */
        [data-testid="stVerticalBlock"] {
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        /* Title */
        h1 {
            color: #d4a017 !important;  /* elegant gold */
            font-size: 2.6em !important;
            margin-bottom: 5px;
            font-weight: 700;
        }

        /* Frosted control panel */
        .control-panel {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.75);
            border: 1px solid rgba(212, 160, 23, 0.4);
            border-radius: 20px;
            padding: 20px 30px;
            backdrop-filter: blur(12px);
            color: #222;
            width: 80%;
            max-width: 600px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }

        /* Labels and text */
        label, .stSelectbox label, .stSlider label {
            color: #222 !important;
            font-weight: 600;
        }

        /* Sliders */
        .stSlider > div > div > div > div {
            background: #d4a017 !important;
        }

        /* Buttons (rounded aesthetic) */
        div.stButton > button {
            background: linear-gradient(to right, #ffe082, #ffd54f);
            color: #222 !important;
            border: none;
            border-radius: 50%;
            width: 80px;
            height: 80px;
            font-size: 1.5em;
            font-weight: 700;
            box-shadow: 0 0 15px rgba(255, 213, 79, 0.6);
        }

        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(255, 213, 79, 0.8);
        }

        /* Download button */
        .download-btn > button {
            background-color: #ffd54f !important;
            color: #222 !important;
            font-weight: 600;
            border-radius: 12px;
            padding: 0.5rem 1.2rem;
            border: none;
        }

        .download-btn > button:hover {
            background-color: #ffecb3 !important;
        }

        /* Info box */
        [data-testid="stInfo"] {
            background-color: #fff9c4 !important;
            color: #444 !important;
            border-left: 5px solid #ffd54f;
            border-radius: 10px;
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
