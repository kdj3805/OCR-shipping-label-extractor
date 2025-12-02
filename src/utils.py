import os
import csv
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------
# IMAGE FILE LOADER
# ---------------------------
def get_image_files(input_dir):
    """Return list of image paths from a folder."""
    exts = (".jpg", ".jpeg", ".png", ".bmp")
    files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(exts)
    ]
    logger.info(f"Found {len(files)} images in {input_dir}")
    return sorted(files)


# ---------------------------
# GROUND TRUTH LOADER
# ---------------------------
def load_ground_truth(csv_path):
    """
    Loads ground truth: CSV format of:
        image_name, ground_truth

    Returns: dict {image_name: label}
    """
    gt = {}
    if not os.path.exists(csv_path):
        logger.error(f"Ground truth file not found: {csv_path}")
        return gt

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            image_name, truth = row[0].strip(), row[1].strip()
            gt[image_name] = truth

    logger.info(f"Loaded {len(gt)} ground truth entries from {csv_path}")
    return gt


# ---------------------------
# ACCURACY CALCULATOR
# ---------------------------
def calculate_accuracy(predictions, truths):
    total = len(truths)
    correct = sum(1 for p, t in zip(predictions, truths) if p == t)
    partial = sum(1 for p, t in zip(predictions, truths) if p and p in t)

    accuracy = (correct / total * 100) if total > 0 else 0
    partial_accuracy = (partial / total * 100) if total > 0 else 0

    return {
        "total_samples": total,
        "exact_matches": correct,
        "partial_matches": partial,
        "accuracy": accuracy,
        "partial_accuracy": partial_accuracy,
        "predictions": predictions,
        "ground_truths": truths,
    }


# ---------------------------
# REPORT GENERATOR
# ---------------------------
def generate_accuracy_report(metrics, output_path):
    lines = []
    lines.append("============================================================")
    lines.append("OCR ACCURACY REPORT")
    lines.append("============================================================")
    lines.append(f"Total Samples: {metrics['total_samples']}")
    lines.append(f"Exact Matches: {metrics['exact_matches']}")
    lines.append(f"Partial Matches: {metrics['partial_matches']}")
    lines.append(f"Exact Accuracy: {metrics['accuracy']:.2f}%")
    lines.append(f"Partial Accuracy: {metrics['partial_accuracy']:.2f}%")
    lines.append("============================================================\n")
    report = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Report saved to {output_path}")
    return report


# ---------------------------
# RESULT SAVER (JSON)
# ---------------------------
def save_results(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info(f"Results saved to {output_path}")


# ---------------------------
# CREATE TIMESTAMPED OUTPUT DIRECTORY
# ---------------------------
def create_output_directory(base_dir="results"):
    """
    Creates a timestamped directory inside base_dir.
    Example:
        create_output_directory("results_fast")
        -> results_fast/20251202_092300
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(base_dir, ts)
    os.makedirs(out_dir, exist_ok=True)

    logger.info(f"Created output directory: {out_dir}")
    return out_dir
