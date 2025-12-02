import os
import cv2
import numpy as np
import pytesseract
import logging
import platform
from typing import List

logger = logging.getLogger(__name__)


class OCREngine:
    def __init__(self, tesseract_path=None, use_easyocr=True):
        # Tesseract path auto-detect
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif platform.system() == "Windows":
            for p in [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    logger.info(f"Using Tesseract from: {p}")
                    break

        # EasyOCR
        self.use_easyocr = use_easyocr
        self.reader = None
        if use_easyocr:
            try:
                import easyocr
                self.reader = easyocr.Reader(["en"], gpu=False)
                logger.info("EasyOCR reader initialized (CPU).")
            except:
                logger.warning("EasyOCR init failed. Using Tesseract only.")
                self.reader = None
                self.use_easyocr = False

        # Best Tesseract configs
        self.tess_configs = [
            "--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "--psm 11 --oem 3",
            "--psm 3 --oem 3",
        ]

    def _generate_variants(self, gray):
        vars = [gray]

        # CLAHE
        try:
            clahe = cv2.createCLAHE(3.0, (8, 8))
            vars.append(clahe.apply(gray))
        except:
            pass

        # Bilateral + Otsu
        try:
            bil = cv2.bilateralFilter(gray, 9, 75, 75)
            _, th = cv2.threshold(bil, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            vars.append(th)
        except:
            pass

        # Adaptive
        for b in [31, 41]:
            try:
                t = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, b, 10)
                vars.append(t)
                vars.append(cv2.bitwise_not(t))
            except:
                pass

        # Sharpen
        try:
            k = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            vars.append(cv2.filter2D(gray, -1, k))
        except:
            pass

        # Close
        try:
            k = np.ones((2, 2), np.uint8)
            vars.append(cv2.morphologyEx(gray, cv2.MORPH_CLOSE, k))
        except:
            pass

        # Deduplicate
        cleaned = []
        seen = set()
        for v in vars:
            vid = v.__array_interface__["data"][0]
            if vid not in seen:
                cleaned.append(v)
                seen.add(vid)

        return cleaned

    def _ocr_tess(self, img):
        texts = []
        for cfg in self.tess_configs:
            try:
                t = pytesseract.image_to_string(img, config=cfg).strip()
                if t:
                    texts.append(t)
            except:
                pass
        return texts

    def _ocr_easy(self, img):
        if not self.use_easyocr or self.reader is None:
            return []
        try:
            rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            res = self.reader.readtext(rgb)
            texts = [t[1] for t in res if t[1]]
            if texts:
                texts.append(" ".join(texts))
            return texts
        except:
            return []

    def ocr_rois(self, rois: List[np.ndarray]) -> List[str]:
        out = []
        for roi in rois:
            gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            vars = self._generate_variants(gray)

            for v in vars:
                out.extend(self._ocr_tess(v))

            out.extend(self._ocr_easy(roi))

        # dedupe
        final = []
        for t in out:
            t = t.strip()
            if t and t not in final:
                final.append(t)

        logger.info(f"OCR produced {len(final)} raw text candidates")
        return final
