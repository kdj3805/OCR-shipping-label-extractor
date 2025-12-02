"""
Audit results file for integrity
"""
import json
from pathlib import Path


def audit_results(results_file):
    """Audit the results file for correctness"""
    
    print(f"\n{'='*80}")
    print("RESULTS FILE AUDIT")
    print(f"{'='*80}")
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data['detailed_results']
    
    # Count categories
    correct_count = 0
    wrong_count = 0
    skipped_count = 0
    partial_count = 0
    
    correct_images = []
    wrong_images = []
    
    for r in results:
        gt = r.get('ground_truth', '')
        pred = r.get('prediction', '')
        
        if gt == 'NO_PATTERN':
            skipped_count += 1
        elif r.get('correct'):
            correct_count += 1
            correct_images.append({
                'name': r['image_name'],
                'text': pred
            })
        else:
            wrong_count += 1
            wrong_images.append({
                'name': r['image_name'],
                'prediction': pred,
                'ground_truth': gt
            })
            
            # Check if partial match
            if pred and gt and ('_1_' in pred or '_1' in pred):
                partial_count += 1
    
    total = correct_count + wrong_count
    accuracy = (correct_count / total * 100) if total > 0 else 0
    
    # Display summary
    print(f"\nFile: {results_file}")
    print(f"\nCounts:")
    print(f"  Total testable:    {total}")
    print(f"  Correct:           {correct_count}")
    print(f"  Wrong:             {wrong_count}")
    print(f"  Skipped (no _1_):  {skipped_count}")
    print(f"  Partial matches:   {partial_count} (in wrong category)")
    print(f"\nCalculated Accuracy: {accuracy:.2f}%")
    print(f"File claims:         {data.get('accuracy', 'N/A'):.2f}%")
    
    # Verify match
    if abs(accuracy - data.get('accuracy', 0)) < 0.01:
        print(f"\n✅ Accuracy calculation VERIFIED")
    else:
        print(f"\n⚠️  Accuracy mismatch!")
    
    # Show correct predictions
    print(f"\n{'='*80}")
    print(f"CORRECT PREDICTIONS ({correct_count}):")
    print(f"{'='*80}")
    for i, img in enumerate(correct_images, 1):
        print(f"{i}. {img['name']:<50} → {img['text']}")
    
    # Show wrong predictions
    print(f"\n{'='*80}")
    print(f"WRONG PREDICTIONS ({wrong_count}):")
    print(f"{'='*80}")
    for i, img in enumerate(wrong_images, 1):
        print(f"{i}. {img['name']}")
        print(f"   Expected: {img['ground_truth']}")
        print(f"   Got:      {img['prediction']}")
        
        # Check similarity
        if img['prediction'] and img['ground_truth']:
            # Simple similarity check
            pred_parts = img['prediction'].split('_1_')
            gt_parts = img['ground_truth'].split('_1_')
            
            if len(pred_parts) == 2 and len(gt_parts) == 2:
                num_pred = pred_parts[0]
                num_gt = gt_parts[0]
                
                # Count matching digits
                matching_digits = sum(1 for p, g in zip(num_pred, num_gt) if p == g)
                if len(num_gt) > 0:
                    digit_accuracy = (matching_digits / len(num_gt) * 100)
                    print(f"   Digit match: {digit_accuracy:.0f}% ({matching_digits}/{len(num_gt)} digits)")
    
    print(f"\n{'='*80}")
    
    return accuracy, correct_count, wrong_count


def compare_with_ground_truth(results_file, ground_truth_file):
    """Compare results with original ground truth file"""
    
    print(f"\n{'='*80}")
    print("CROSS-CHECK WITH GROUND TRUTH FILE")
    print(f"{'='*80}")
    
    # Load results
    with open(results_file, 'r') as f:
        results_data = json.load(f)
    results = {r['image_name']: r for r in results_data['detailed_results']}
    
    # Load ground truth
    import csv
    ground_truth = {}
    with open(ground_truth_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ground_truth'] != 'NO_PATTERN':
                ground_truth[row['image_name']] = row['ground_truth']
    
    print(f"\nGround truth entries: {len(ground_truth)}")
    print(f"Results entries:      {len([r for r in results.values() if r.get('ground_truth') != 'NO_PATTERN'])}")
    
    # Check each entry
    matches = 0
    mismatches = []
    
    for img_name, gt_text in ground_truth.items():
        if img_name in results:
            result = results[img_name]
            pred = result.get('prediction', '')
            
            if pred == gt_text:
                matches += 1
            else:
                mismatches.append({
                    'image': img_name,
                    'ground_truth': gt_text,
                    'prediction': pred
                })
    
    accuracy = (matches / len(ground_truth) * 100) if len(ground_truth) > 0 else 0
    
    print(f"\nMatches:     {matches}/{len(ground_truth)}")
    print(f"Mismatches:  {len(mismatches)}/{len(ground_truth)}")
    print(f"Accuracy:    {accuracy:.2f}%")
    
    if mismatches:
        print(f"\nMismatches:")
        for m in mismatches[:5]:  # Show first 5
            print(f"  {m['image']}")
            print(f"    GT:   {m['ground_truth']}")
            print(f"    Pred: {m['prediction']}")
    
    print(f"{'='*80}")
    
    return accuracy


def main():
    results_file = "results/final_submission_results.json"
    ground_truth_file = "data/ground_truth.csv"
    
    if not Path(results_file).exists():
        print(f"❌ Results file not found: {results_file}")
        return
    
    # Audit results file
    accuracy, correct, wrong = audit_results(results_file)
    
    # Cross-check with ground truth
    if Path(ground_truth_file).exists():
        print("\n")
        gt_accuracy = compare_with_ground_truth(results_file, ground_truth_file)
    
    print(f"\n{'='*80}")
    print("AUDIT SUMMARY")
    print(f"{'='*80}")
    print(f"Results file shows:  {accuracy:.2f}% ({correct}/{correct+wrong})")
    if Path(ground_truth_file).exists():
        print(f"Ground truth check:  {gt_accuracy:.2f}%")
    
    if accuracy >= 75:
        print(f"\n✅ TARGET ACHIEVED: {accuracy:.2f}% >= 75%")
    else:
        print(f"\n⚠️  Below target: {accuracy:.2f}% < 75%")
    
    print(f"{'='*80}")


if __name__ == "__main__":
    main()