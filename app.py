import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io

# --- Streamlit Page Config ---
st.set_page_config(page_title="Filterly", layout="centered")

# --- Dark Brown & Gold Theme CSS ---
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(to bottom right, #FFFDF5, #FFF8E1);
            color: #4E342E;
        }
        [data-testid="stSidebar"] {
            background-color: #FFECB3 !important;
            color: #4E342E !important;
        }
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] div {
            color: #4E342E !important;
        }
        h1, h2, h3, h4 {
            color: #C89B00 !important;
            font-weight: 700;
        }
        div.stButton > button {
            background: linear-gradient(to right, #FFD54F, #FFC107);
            color: #4E342E;
            border-radius: 10px;
            border: 1px solid #C89B00;
            font-weight: 600;
        }
        div.stButton > button:hover {
            background: linear-gradient(to right, #FFC107, #FFB300);
            color: #4E342E;
            border: 1px solid #B58900;
        }
        button[data-baseweb="tab"] {
            background-color: #FFECB3;
            color: #4E342E;
            border-radius: 10px;
            font-weight: 600;
        }
        button[data-baseweb="tab"]:hover {
            background-color: #FFD54F;
            color: #4E342E;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #FFC107;
            color: #4E342E;
            border-bottom: 3px solid #C89B00;
        }
        [data-testid="stInfo"] {
            background-color: #FFF8E1;
            color: #4E342E;
            border-left: 5px solid #FFD54F;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("Filterly")

# --- Sidebar Filters & Adjustments ---
st.sidebar.header("Filters & Adjustments")
filter_name = st.sidebar.selectbox(
    "Choose a filter:",
    ["none", "grayscale", "sepia", "invert", "blur", "sharpen", "edge", "emboss", "contour"]
)
brightness = st.sidebar.slider("Brightness", 0, 200, 100)
contrast = st.sidebar.slider("Contrast", 0, 200, 100)
intensity = st.sidebar.slider("Filter Intensity (for blur/sharpen)", 1, 10, 2)

# --- Sidebar Transformations ---
st.sidebar.header("Transformations")
rotate_angle = st.sidebar.slider("Rotate (degrees)", 0, 360, 0)
flip_horizontal = st.sidebar.checkbox("Flip Horizontally")
flip_vertical = st.sidebar.checkbox("Flip Vertically")

st.sidebar.subheader("Crop Image")
crop_x = st.sidebar.slider("Crop X (left %)", 0, 100, 0)
crop_y = st.sidebar.slider("Crop Y (top %)", 0, 100, 0)
crop_width = st.sidebar.slider("Crop Width (%)", 10, 100, 100)
crop_height = st.sidebar.slider("Crop Height (%)", 10, 100, 100)

# --- Helper function ---
def apply_filter(frame, filter_name, brightness=100, contrast=100, intensity=2,
                 rotate_angle=0, flip_h=False, flip_v=False,
                 crop_x=0, crop_y=0, crop_width=100, crop_height=100):

    frame = np.array(frame)
    
    # Brightness & contrast
    pil_img = Image.fromarray(frame)
    pil_img = ImageEnhance.Brightness(pil_img).enhance(brightness / 100)
    pil_img = ImageEnhance.Contrast(pil_img).enhance(contrast / 100)

    # Filters
    if filter_name == "grayscale":
        frame = np.dot(np.array(pil_img)[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
        pil_img = Image.fromarray(np.stack([frame]*3, axis=-1))
    elif filter_name == "sepia":
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        frame = np.array(pil_img)
        frame = np.dot(frame, kernel.T)
        frame = np.clip(frame, 0, 255).astype(np.uint8)
        pil_img = Image.fromarray(frame)
    elif filter_name == "invert":
        pil_img = Image.fromarray(255 - np.array(pil_img))
    elif filter_name == "blur":
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(intensity))
    elif filter_name == "sharpen":
        for _ in range(intensity):
            pil_img = pil_img.filter(ImageFilter.SHARPEN)
    elif filter_name == "edge":
        pil_img = pil_img.filter(ImageFilter.FIND_EDGES)
    elif filter_name == "emboss":
        pil_img = pil_img.filter(ImageFilter.EMBOSS)
    elif filter_name == "contour":
        pil_img = pil_img.filter(ImageFilter.CONTOUR)

    # Transformations
    if rotate_angle != 0:
        pil_img = pil_img.rotate(rotate_angle, expand=True)
    if flip_h:
        pil_img = pil_img.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v:
        pil_img = pil_img.transpose(Image.FLIP_TOP_BOTTOM)

    # Crop
    width, height = pil_img.size
    left = int(width * crop_x / 100)
    top = int(height * crop_y / 100)
    right = left + int(width * crop_width / 100)
    bottom = top + int(height * crop_height / 100)
    pil_img = pil_img.crop((left, top, min(right, width), min(bottom, height)))

    return pil_img

# --- Image input ---
st.subheader("📷 Capture or Upload an Image")
tab1, tab2 = st.tabs(["📸 Use Camera", "📂 Upload Image"])
image = None

with tab1:
    img_file_buffer = st.camera_input("Take a photo")
    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)

with tab2:
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)

# --- Process and display ---
if image is not None:
    with st.spinner("Applying filters and transformations..."):
        filtered_image = apply_filter(
            image, filter_name, brightness, contrast, intensity,
            rotate_angle, flip_horizontal, flip_vertical,
            crop_x, crop_y, crop_width, crop_height
        )

    # --- Show only filtered image initially ---
    st.subheader("Filtered Image")
    st.image(filtered_image, use_container_width=True)

    # --- Before/After comparison with slider ---
    st.subheader("🔄 Compare Original vs Filtered")
    
    # Resize original to match filtered image
    orig_resized = image.resize(filtered_image.size)
    orig_np = np.array(orig_resized).astype(np.float32)
    filt_np = np.array(filtered_image).astype(np.float32)

    # Slider for blending
    alpha = st.slider("Reveal Original vs Filtered", 0.0, 1.0, 0.0, 0.01)  # 0 = filtered, 1 = original
    blended = (alpha * orig_np + (1 - alpha) * filt_np).astype(np.uint8)
    st.image(blended, use_container_width=True)

    # --- Download button ---
    buf = io.BytesIO()
    filtered_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(
        label="Download Filtered Image",
        data=byte_im,
        file_name="filtered_snapshot.png",
        mime="image/png"
    )
else:
    st.info("📸 Take a photo or upload an image to apply filters.")
