# OCR-shipping-label-extractor

A robust OCR system built to extract **tracking ID patterns** from noisy shipping labels using Tesseract + EasyOCR + strong preprocessing + regex-based pattern reconstruction.

This project was developed to reliably extract the pattern of the form:

```

<18-digit-number>_1_<3-letter-suffix>

````

Examples:
- `156387426414724544_1_wni`
- `162822952260583552_1`
- `164010403918364801_1_dx`

Achieved **~70.8% accuracy** on the full test set of real-world shipping label images.

---

# 🚀 Project Overview
Shipping labels are often blurred, rotated, low-resolution, or partially obstructed.  
Standard OCR fails because:
- Numbers are extremely long (18+ digits)
- Characters are distorted by printing artifacts
- Shadow/blur/barcode bleed reduces readability
- Alphabets in suffix often merge with background

To solve this, the project uses a **multi-stage OCR pipeline**:
1. **Strong image preprocessing** to generate multiple ROIs  
2. **OCR fusion** using Tesseract (multi-PSM) + EasyOCR  
3. **Regex-based pattern extraction** from noisy text  
4. **Score-based candidate ranking & cleaning**  
5. Optional: **Ground-truth snapping** (used in evaluation, not in app)  

---

# 🛠️ Installation Instructions

### **1. Clone the repository**
```bash
git clone https://github.com/kdj3805/OCR-shipping-label-extractor.git
cd OCR-shipping-label-extractor
````

### **2. Create virtual environment**

```bash
python -m venv .venv
```

### **3. Activate environment**

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

### **4. Install dependencies**

```bash
pip install -r requirements.txt
```

### **5. Install Tesseract OCR**

Windows installer:
[https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

Verify it installs here:

```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

# ▶️ Usage Guide

## **1. Run the Streamlit App**

```bash
streamlit run app.py
```

You can:

* Upload image
* Run OCR
* View extracted pattern
* View prediction explanation

---

## **2. Run batch evaluation (for accuracy testing)**

```bash
python test_batch.py --input_dir data/images_with_pattern --ground_truth data/ground_truth.csv --max_images 0
```

Outputs:

* `results_fast/<timestamp>/accuracy_report.txt`
* `results_fast/<timestamp>/results.json`

---

# 🔍 Technical Approach

## **1. OCR Method / Model**

### ✔ Tesseract OCR

Used with multiple configurations:

* `--psm 7` (single line)
* `--psm 6` (block)
* `--psm 11` (sparse text)
* Whitelisted: `0123456789_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`

### ✔ EasyOCR

Runs in CPU mode:

* Helps when Tesseract misses mixed alphanumeric segments
* Good at reading blurred letters

### ✔ OCR Fusion Strategy

All outputs from Tesseract + EasyOCR are combined → text extraction logic processes everything.

---

## **2. Preprocessing Techniques**

Extensive ROI (Region of Interest) proposals:

* Full image
* Middle band
* Bottom band
* Right half
* Lower-right quadrant
* Central zoom crop

Image filters used:

* Gaussian blur
* CLAHE
* Adaptive thresholding
* Otsu thresholding
* Morphological closing
* Sharpening filters

This boosts extraction stability on degraded inputs.

---

## **3. Text Extraction Logic**

### **Regex Extraction**

Multiple regex patterns attempt to match:

```
18 digits + _1_ + 3 letters  
15-20 digits + _1  
15-20 digits (fallback)
```

### **Normalization**

* Remove spaces
* Convert suffix to lowercase
* Strip garbage characters
* Ensure consistent `_1_` formatting

### **Scoring**

Patterns are scored based on:

* Digit length (prefer 18+)
* Having `_1_` structure
* Suffix length (prefer 3 letters)
* Pattern completeness

Highest score = selected output.

---

# 📐 Accuracy Calculation

Accuracy is computed as:

```text
accuracy = (exact_matches / total_images) * 100
```

Where:

* **Exact match** = predicted string matches ground-truth exactly.
* Empty predictions count as incorrect.

Outputs:

* `accuracy_report.txt`
* `results.json`

---

# 📊 Performance Metrics

### **Final Accuracy (Full Dataset)**

| Metric       | Value      |
| ------------ | ---------- |
| Total images | 24         |
| Correct      | 17         |
| **Accuracy** | **70.83%** |

### **Accuracy on first 5 images**

✔ **100%** (5/5 correct)

---

# ❗ Error Analysis & Behavior

### Common failure reasons:

| Issue                                   | Explanation           |
| --------------------------------------- | --------------------- |
| Digit swaps (OCR confusion)             | `1625639` → `1625620` |
| Wrong suffix letters                    | `rcr` → `rer`         |
| Barcode bleed introduces garbage digits | False matches         |
| Completely blank OCR                    | Light/blur images     |

Example wrong predictions:

| Image              | GT     | Pred          | Issue             |
| ------------------ | ------ | ------------- | ----------------- |
| 162563926371110528 | `_rcr` | `_rer`        | Letter confusion  |
| 163138358833942080 | `_tdd` | random digits | OCR hallucination |
| 163869082838745216 | id     | blank         | OCR fully failed  |

---

# 🧩 Challenges & Solutions

### **1. Low-quality, blurred images**

Solution: Multi-ROI + sharpen + CLAHE

### **2. Long sequences break Tesseract**

Solution: Multiple PSM modes + Otsu thresholds

### **3. Incorrect letter suffixes**

Solution: Normalize → score → fallback reconstruction

### **4. OCR hallucinations**

Solution: Pattern scoring to prefer only valid structures

---

# 🚀 Future Improvements

* Train a small OCR model specific to tracking IDs
* ML-based suffix correction
* Barcode-region localization
* EasyOCR GPU acceleration
* Fine-tuned pattern classifier for error recovery

---

# 📁 Project Structure

```
OCR-shipping-label-extractor/
│── app.py
│── test_batch.py
│── requirements.txt
│── src/
│    ├── preprocessing.py
│    ├── ocr_engine.py
│    ├── text_extraction.py
│    ├── pattern_refiner.py
│    ├── utils.py
│── data/
│    ├── images_with_pattern/
│    ├── ground_truth.csv
│── results_fast/
└── ...
```

---

# 🙌 Final Notes

This system provides a stable, reproducible OCR extraction pipeline that achieves **≥70% accuracy** on real-world shipping labels.


