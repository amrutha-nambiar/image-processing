import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance
import io

# --- Streamlit Page Config ---
st.set_page_config(page_title="📸 Web Camera Filters", layout="centered")

st.title("📸 Camera Filters with Sliders")

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
    # Convert PIL to NumPy
    frame = np.array(frame)

    # Brightness and contrast adjustment
    pil_img = Image.fromarray(frame)
    enhancer_brightness = ImageEnhance.Brightness(pil_img)
    pil_img = enhancer_brightness.enhance(brightness / 100)
    enhancer_contrast = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer_contrast.enhance(contrast / 100)
    frame = np.array(pil_img)

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
        frame = np.array(Image.fromarray(frame).filter(Image.Filter.BLUR))

    return Image.fromarray(frame)

# --- Camera Input ---
img_file_buffer = st.camera_input("📷 Take a photo")

if img_file_buffer is not None:
    # Convert captured image to PIL
    image = Image.open(img_file_buffer)
    st.image(image, caption="Original Image", use_container_width=True)

    # Apply filter
    filtered_image = apply_filter(image, filter_name, brightness, contrast)

    st.image(filtered_image, caption=f"Filtered: {filter_name}", use_container_width=True)

    # --- Download filtered snapshot ---
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
    st.info("📸 Use the camera above to take a photo and apply filters.")
