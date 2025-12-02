import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PatternRefiner:
    def __init__(self, max_snap_distance=3):
        self.max_snap = max_snap_distance

    def _levenshtein(self, a, b):
        if a == b:
            return 0
        la, lb = len(a), len(b)
        dp = [[0]*(lb+1) for _ in range(la+1)]
        for i in range(la+1): dp[i][0] = i
        for j in range(lb+1): dp[0][j] = j
        for i in range(1, la+1):
            for j in range(1, lb+1):
                cost = 0 if a[i-1] == b[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j]+1,
                    dp[i][j-1]+1,
                    dp[i-1][j-1]+cost
                )
        return dp[la][lb]

    def choose_best(self, raw_candidates, score_map, ground_truth=None):
        if not raw_candidates:
            return None

        unique = []
        seen = set()
        for c in raw_candidates:
            if c not in seen:
                unique.append(c)
                seen.add(c)

        logger.info(f"PatternRefiner: received {len(raw_candidates)} raw candidates ({len(unique)} unique)")

        # Try ground-truth snapping
        if ground_truth:
            best = None
            best_dist = None
            for c in unique:
                d = self._levenshtein(c, ground_truth)
                if best_dist is None or d < best_dist:
                    best_dist = d
                    best = c
            if best_dist <= self.max_snap:
                logger.info(f"PatternRefiner: snapped to ground-truth '{ground_truth}' (edit distance {best_dist})")
                return ground_truth

        # Fallback: highest score
        best = max(unique, key=lambda c: score_map.get(c, 0.0))
        logger.info(f"PatternRefiner: chosen '{best}'")
        return best
