# src/barcode_reader.py
"""
Barcode reader utility using pyzbar (1D/2D barcodes).
"""

import logging
import re
from typing import List, Iterable, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None
    logger.warning("pyzbar not installed. Barcode decoding will be disabled.")


class BarcodeReader:
    """Lightweight barcode reader wrapper."""

    def __init__(self):
        if pyzbar is None:
            logger.warning("BarcodeReader initialized without pyzbar.")

    def _decode_single(self, image: np.ndarray) -> List[str]:
        if pyzbar is None:
            return []
        try:
            decoded = pyzbar.decode(image)
            texts = []
            for obj in decoded:
                try:
                    txt = obj.data.decode("utf-8", errors="ignore")
                    if txt:
                        texts.append(txt)
                except Exception:
                    continue
            return texts
        except Exception as e:
            logger.error(f"pyzbar.decode failed: {e}")
            return []

    def decode_texts(self, images: Iterable[np.ndarray]) -> List[str]:
        """
        Decode raw barcode texts from one or more images.
        """
        all_texts: List[str] = []
        for img in images:
            if img is None or img.size == 0:
                continue
            texts = self._decode_single(img)
            all_texts.extend(texts)
        # Deduplicate
        unique = list(dict.fromkeys(all_texts).keys())
        if unique:
            logger.info(f"BarcodeReader: decoded {len(unique)} unique strings")
        return unique

    def decode_digits(self, images: Iterable[np.ndarray]) -> List[str]:
        """
        From decoded texts, extract numeric candidates (long digit sequences).
        """
        texts = self.decode_texts(images)
        candidates: List[str] = []
        for t in texts:
            for m in re.findall(r"\d{10,}", t):
                if len(m) >= 15:  # focus on long tracking IDs
                    candidates.append(m)

        # Unique, sorted by length desc
        unique = sorted(set(candidates), key=lambda x: (-len(x), x))
        if unique:
            logger.info(f"BarcodeReader: {len(unique)} numeric candidates; longest len={len(unique[0])}")
        else:
            logger.info("BarcodeReader: no numeric candidates found")
        return unique

    def choose_best_number(self, candidates: List[str]) -> Optional[str]:
        """
        Choose best tracking number: prefer 18 digits, else longest.
        """
        if not candidates:
            return None
        exact_18 = [c for c in candidates if len(c) == 18]
        if exact_18:
            return exact_18[0]
        # Otherwise, longest
        return max(candidates, key=len)
