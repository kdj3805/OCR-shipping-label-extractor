import streamlit as st
import numpy as np
import cv2
import os

from src.preprocessing import ImagePreprocessor
from src.ocr_engine import OCREngine
from src.text_extraction import TextExtractor

# -------------------------------------------------------------
# Title
# -------------------------------------------------------------
st.set_page_config(page_title="OCR Shipping Label Extractor", layout="centered")
st.title("📦 OCR Shipping Label Extractor")
st.write("Upload a label image to extract the tracking pattern.")

# -------------------------------------------------------------
# Initialize pipeline components (same as batch)
# -------------------------------------------------------------
pre = ImagePreprocessor()
ocr_engine = OCREngine(use_easyocr=True)
extractor = TextExtractor()          # no GT snapping for submission


# -------------------------------------------------------------
# Helper: Process uploaded image
# -------------------------------------------------------------
def run_inference(image_path: str) -> str:
    """Runs the full OCR → extraction pipeline on a single image."""

    rois = pre.get_candidate_rois(image_path)
    if not rois:
        return ""

    ocr_texts = ocr_engine.ocr_rois(rois)

    pattern = extractor.extract_best_from_texts(ocr_texts, image_name=None)

    return pattern if pattern else ""


# -------------------------------------------------------------
# UI — Upload image
# -------------------------------------------------------------
uploaded = st.file_uploader(
    "Upload shipping label image",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False
)

# -------------------------------------------------------------
# Run OCR button
# -------------------------------------------------------------
run_ocr = st.button("🔍 Run OCR Extraction")

# -------------------------------------------------------------
# If user uploads an image & clicks button
# -------------------------------------------------------------
if uploaded is not None:
    st.image(uploaded, caption="Uploaded Image", use_column_width=True)

    # Save temp copy for OpenCV
    temp_path = "temp_uploaded_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())

    if run_ocr:   # <-- PROCESS ONLY WHEN BUTTON IS CLICKED
        st.info("🔍 Running OCR... please wait (CPU mode)...")

        # Run OCR pipeline
        pattern = run_inference(temp_path)

        # Display result
        if pattern:
            st.success(f"✅ **Extracted Pattern:** `{pattern}`")
        else:
            st.error("❌ No valid pattern could be extracted from the image.")

        # Cleanup temp
        if os.path.exists(temp_path):
            os.remove(temp_path)

else:
    st.info("📤 Please upload an image to begin.")
