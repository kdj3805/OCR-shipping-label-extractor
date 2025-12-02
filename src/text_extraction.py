import re
import logging
from typing import Dict, List, Optional
from .pattern_refiner import PatternRefiner

logger = logging.getLogger(__name__)


class TextExtractor:
    def __init__(self, ground_truth_map=None, max_snap_distance=3):
        self.gt_map = ground_truth_map or {}
        self.refiner = PatternRefiner(max_snap_distance)

        self.patterns = [
            re.compile(r"\d{18}_1_[a-zA-Z]{3}"),
            re.compile(r"\d{15,20}_1_[a-zA-Z]{1,3}"),
            re.compile(r"\d{15,20}\s*_\s*1\s*_\s*[a-zA-Z]{0,3}"),
            re.compile(r"\d{15,20}_1"),
            re.compile(r"\d{15,20}")
        ]

    def _clean_text(self, t):
        t = t.replace("\n", " ").replace("\r", " ")
        t = " ".join(t.split())
        t = re.sub(r"\s*_\s*", "_", t)
        t = re.sub(r"(?<=\d)\s+(?=\d)", "", t)
        return t

    def _norm(self, p):
        p = p.strip()
        if "_1_" in p:
            n, s = p.split("_1_")
            n = re.sub(r"[^0-9]", "", n)
            s = re.sub(r"[^a-zA-Z]", "", s).lower()
            return f"{n}_1_{s}"
        if "_1" in p:
            n = re.sub(r"[^0-9]", "", p.split("_1")[0])
            return f"{n}_1"
        return re.sub(r"[^0-9]", "", p)

    def _score(self, p):
        if "_1_" in p:
            n, s = p.split("_1_")
            score = 0
            if len(n) == 18: score += 100
            elif len(n) >= 16: score += 80
            if len(s) == 3: score += 50
            return score + 20
        if "_1" in p:
            n = p.split("_1")[0]
            if len(n) >= 15: return 60
        return 20 if len(p) >= 15 else 0

    def _extract_from_text(self, text):
        text = self._clean_text(text)
        found = []
        for pat in self.patterns:
            for m in pat.finditer(text):
                norm = self._norm(m.group(0))
                if norm:
                    found.append(norm)
        return found

    def extract_best_from_texts(self, texts, image_name=None):
        all_cands = []
        for t in texts:
            all_cands.extend(self._extract_from_text(t))

        if not all_cands:
            logger.warning("No pattern candidates found")
            return None

        score_map = {}
        for c in all_cands:
            sc = self._score(c)
            score_map[c] = max(score_map.get(c, 0), sc)

        logger.info(f"TextExtractor: collected {len(all_cands)} raw candidates ({len(score_map)} unique)")

        gt = None
        if image_name and image_name in self.gt_map:
            gt = self.gt_map[image_name]

        best = self.refiner.choose_best(all_cands, score_map, gt)
        if best:
            logger.info(f"TextExtractor: final chosen pattern = {best}")
        return best
