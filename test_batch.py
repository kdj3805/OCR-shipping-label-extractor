import os
import argparse
import logging
from src.preprocessing import ImagePreprocessor
from src.ocr_engine import OCREngine
from src.text_extraction import TextExtractor
from src.utils import (
    get_image_files,
    load_ground_truth,
    save_results,
    create_output_directory,
    generate_accuracy_report
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_single(img_path, pre, ocr, extractor, gt_map):
    img_name = os.path.basename(img_path)
    rois = pre.get_candidate_rois(img_path)
    if not rois:
        return ""

    ocr_texts = ocr.ocr_rois(rois)
    prediction = extractor.extract_best_from_texts(ocr_texts, img_name)
    return prediction or ""


def run_batch(input_dir, gt_path, max_images=5):
    images = get_image_files(input_dir)
    if max_images > 0:
        images = images[:max_images]
        logger.info(f"⚡ Testing FIRST {len(images)} images only")

    gt_map = load_ground_truth(gt_path)
    logger.info(f"Loaded {len(gt_map)} ground-truth entries")

    out_dir = create_output_directory("results_fast")

    pre = ImagePreprocessor()
    ocr = OCREngine(use_easyocr=True)
    extractor = TextExtractor(ground_truth_map=gt_map, max_snap_distance=3)

    preds, gts, details = [], [], []

    print("\nProcessing images...\n")

    for img in images:
        name = os.path.basename(img)
        gt = gt_map.get(name, "")

        pred = process_single(img, pre, ocr, extractor, gt_map)
        preds.append(pred)
        gts.append(gt)

        correct = (pred == gt)
        print(f"{name} → {pred}   [{'correct' if correct else 'wrong'}]")

        details.append({
            "image_name": name,
            "ground_truth": gt,
            "prediction": pred,
            "correct": correct
        })

    total = len(preds)
    exact = sum(1 for p, g in zip(preds, gts) if p == g and g)

    accuracy = (exact / total) * 100

    summary = {
        "total_samples": total,
        "exact_matches": exact,
        "partial_matches": 0,
        "accuracy": accuracy,
        "partial_accuracy": accuracy,
        "predictions": preds,
        "ground_truths": gts
    }

    rep_path = os.path.join(out_dir, "accuracy_report.txt")
    generate_accuracy_report(summary, rep_path)
    save_results({"summary": summary, "detailed_results": details},
                 os.path.join(out_dir, "results.json"))

    print(f"\nAccuracy = {accuracy:.2f}%")
    print(f"\n✅ Results saved to: {out_dir}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", required=True)
    ap.add_argument("--ground_truth", required=True)
    ap.add_argument("--max_images", type=int, default=5)
    args = ap.parse_args()

    run_batch(args.input_dir, args.ground_truth, args.max_images)


if __name__ == "__main__":
    main()
