import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io

# --- Streamlit Page Config ---
st.set_page_config(page_title="Filterly", layout="centered")

# --- Gold & White Theme CSS ---
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {background: linear-gradient(to bottom right, #FFFDF5, #FFF8E1); color: black;}
        [data-testid="stSidebar"] {background-color: #FFECB3 !important; color: black !important;}
        h1, h2, h3, h4 {color: #C89B00 !important; font-weight: 700;}
        div.stButton > button {background: linear-gradient(to right, #FFD54F, #FFC107); color: black; border-radius: 10px; border: 1px solid #C89B00; font-weight: 600;}
        div.stButton > button:hover {background: linear-gradient(to right, #FFC107, #FFB300);}
    </style>
""", unsafe_allow_html=True)

st.title("Filterly")

# --- Sidebar controls ---
st.sidebar.header("Filters & Adjustments")
filter_name = st.sidebar.selectbox(
    "Choose a filter:",
    ["none", "grayscale", "sepia", "invert", "blur", "sharpen", "edge", "emboss", "contour"]
)

brightness = st.sidebar.slider("Brightness", 0, 200, 100)
contrast = st.sidebar.slider("Contrast", 0, 200, 100)
intensity = st.sidebar.slider("Filter Intensity (for blur/sharpen)", 1, 10, 2)

# --- Image transformation controls ---
st.sidebar.header("Transformations")
rotate_angle = st.sidebar.slider("Rotate (degrees)", 0, 360, 0)
flip_horizontal = st.sidebar.checkbox("Flip Horizontally")
flip_vertical = st.sidebar.checkbox("Flip Vertically")

st.sidebar.subheader("Crop Image")
crop_x = st.sidebar.slider("Crop X (left to right %)", 0, 100, 0)
crop_y = st.sidebar.slider("Crop Y (top to bottom %)", 0, 100, 0)
crop_width = st.sidebar.slider("Crop Width (%)", 10, 100, 100)
crop_height = st.sidebar.slider("Crop Height (%)", 10, 100, 100)

# --- Helper function for filters and transformations ---
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

    # --- Transformations ---
    if rotate_angle != 0:
        pil_img = pil_img.rotate(rotate_angle, expand=True)
    if flip_h:
        pil_img = pil_img.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v:
        pil_img = pil_img.transpose(Image.FLIP_TOP_BOTTOM)

    # --- Crop ---
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

    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Original Image", use_container_width=True)
    with col2:
        st.image(filtered_image, caption=f"Filtered & Transformed: {filter_name}", use_container_width=True)

    # --- Before/After Slider ---
    st.subheader("🔄 Compare Before / After")
    st.image([image, filtered_image], caption=["Original", "Filtered"], width=300)

    # --- Download ---
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
