import cv2
import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Strong ROI generator for degraded shipping labels.
    """

    def __init__(self, max_width: int = 1600):
        self.max_width = max_width

    def _load_image(self, path: str):
        img = cv2.imread(path)
        if img is None:
            logger.error(f"Failed to load: {path}")
        return img

    def _resize(self, img):
        h, w = img.shape[:2]
        if w <= self.max_width:
            return img
        scale = self.max_width / w
        return cv2.resize(img, (self.max_width, int(h * scale)), cv2.INTER_CUBIC)

    def _gray(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img

    def _normalize(self, gray):
        return cv2.GaussianBlur(gray, (3, 3), 0)

    def get_candidate_rois(self, path: str) -> List[np.ndarray]:
        img = self._load_image(path)
        if img is None:
            return []

        img = self._resize(img)
        gray = self._normalize(self._gray(img))
        h, w = gray.shape[:2]

        rois = [
            gray,
            gray[int(h*0.30):int(h*0.60), :],
            gray[int(h*0.60):h, :],
            gray[:, int(w*0.45):w],
            gray[int(h*0.60):h, int(w*0.45):w],
            gray[int(h*0.25):int(h*0.75), int(w*0.15):int(w*0.85)]
        ]

        valid = [r for r in rois if r is not None and r.size > 0]
        logger.info(f"Preprocessing created {len(valid)} ROI entries")
        return valid
