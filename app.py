import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io

# --- Streamlit Page Config ---
st.set_page_config(page_title="Filterly", layout="centered")

# --- Modern Gold & White Theme CSS ---
st.markdown("""
    <style>
        /* App background */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(to bottom right, #ffffff, #f9f6f2);
            color: #1c1c1c;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f5f3ef !important;
            border-right: 1px solid #e0d9c8;
        }

        /* Sidebar text */
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div {
            color: #1c1c1c !important;
            font-weight: 500;
        }

        /* Titles */
        h1, h2, h3, h4 {
            color: #b8860b !important; /* muted gold */
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        /* Buttons */
        div.stButton > button {
            background: #f5de9e;
            color: #1c1c1c;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            padding: 0.5rem 1rem;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
            transition: all 0.2s ease-in-out;
        }

        div.stButton > button:hover {
            background: #e8c97a;
            color: #000;
            box-shadow: 0px 3px 6px rgba(0,0,0,0.15);
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            background-color: #faf9f7;
            color: #1c1c1c;
            border-radius: 6px;
            border: 1px solid #e0d9c8;
            font-weight: 500;
            padding: 0.4rem 0.8rem;
        }

        button[data-baseweb="tab"]:hover {
            background-color: #f5de9e;
            color: #000;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #e8c97a;
            color: #000;
            border-bottom: 2px solid #b8860b;
        }

        /* Info boxes */
        [data-testid="stInfo"] {
            background-color: #f9f6f2;
            color: #1c1c1c;
            border-left: 4px solid #b8860b;
        }

        /* Image styling */
        [data-testid="stImageContainer"] img {
            border-radius: 10px;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
        }

        /* Sliders */
        .stSlider > div > div > div > div {
            background: #b8860b;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("✨ Filterly")

st.caption("A clean and elegant image filter app")

# --- Sidebar controls ---
st.sidebar.header("🎛️ Filters & Adjustments")
filter_name = st.sidebar.selectbox(
    "Choose a filter:",
    ["none", "grayscale", "sepia", "invert", "blur", "sharpen", "edge", "emboss", "contour"]
)

brightness = st.sidebar.slider("Brightness", 0, 200, 100)
contrast = st.sidebar.slider("Contrast", 0, 200, 100)
intensity = st.sidebar.slider("Filter Intensity (for blur/sharpen)", 1, 10, 2)

# --- Helper function for filters ---
def apply_filter(frame, filter_name, brightness=100, contrast=100, intensity=2):
    frame = np.array(frame)

    # Brightness & contrast
    pil_img = Image.fromarray(frame)
    enhancer_brightness = ImageEnhance.Brightness(pil_img)
    pil_img = enhancer_brightness.enhance(brightness / 100)
    enhancer_contrast = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer_contrast.enhance(contrast / 100)
    frame = np.array(pil_img)

    # Filters
    if filter_name == "grayscale":
        frame = np.dot(frame[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        frame = np.stack([frame] * 3, axis=-1)
    elif filter_name == "sepia":
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        frame = frame.dot(kernel.T)
        frame = np.clip(frame, 0, 255).astype(np.uint8)
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

# --- Image input options ---
st.subheader("📷 Capture or Upload an Image")

tab1, tab2 = st.tabs(["Use Camera", "Upload Image"])

image = None

with tab1:
    img_file_buffer = st.camera_input("Take a photo")
    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)

with tab2:
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

# --- Process image if available ---
if image is not None:
    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Original", use_container_width=True)

    with col2:
        filtered_image = apply_filter(image, filter_name, brightness, contrast, intensity)
        st.image(filtered_image, caption=f"Filtered: {filter_name}", use_container_width=True)

    # --- Download filtered image ---
    buf = io.BytesIO()
    filtered_image.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="💾 Download Filtered Image",
        data=byte_im,
        file_name="filtered_snapshot.png",
        mime="image/png"
    )
else:
    st.info("Take a photo or upload an image to apply filters.")
