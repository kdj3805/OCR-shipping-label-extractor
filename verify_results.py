"""
Verify results by showing images with predictions
This allows visual verification that predictions match what's actually in images
"""
import json
import cv2
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np


def verify_results(results_file, images_dir, show_all=False):
    """
    Visually verify results by showing images with predictions
    
    Args:
        results_file: Path to results JSON
        images_dir: Path to images directory
        show_all: If True, show all results. If False, show only correct ones for verification
    """
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data['detailed_results']
    
    # Filter results
    if show_all:
        to_verify = results
        title = "ALL RESULTS"
    else:
        to_verify = [r for r in results if r.get('correct') and r.get('ground_truth') != 'NO_PATTERN']
        title = "CORRECT PREDICTIONS (for verification)"
    
    print(f"\n{'='*80}")
    print(title)
    print(f"{'='*80}")
    print(f"Total to verify: {len(to_verify)}")
    print("\nFor each image:")
    print("  - Look at the image")
    print("  - Check if the prediction matches what you SEE in the image")
    print("  - Press 'y' if correct, 'n' if wrong")
    print("  - Press 'q' to quit")
    print(f"{'='*80}")
    
    input("\nPress ENTER to start verification...")
    
    verified_correct = 0
    verified_wrong = 0
    issues = []
    
    for i, result in enumerate(to_verify, 1):
        img_name = result['image_name']
        prediction = result['prediction']
        ground_truth = result['ground_truth']
        
        img_path = Path(images_dir) / img_name
        
        if not img_path.exists():
            print(f"\n❌ Image not found: {img_name}")
            continue
        
        # Load and display image
        img = cv2.imread(str(img_path))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        ax.imshow(img_rgb)
        ax.axis('off')
        
        # Add prediction info
        info_text = f"[{i}/{len(to_verify)}] {img_name}\n\nPrediction: {prediction}"
        fig.text(0.5, 0.02, info_text, ha='center', fontsize=14, 
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)
        
        print(f"\n{'='*80}")
        print(f"[{i}/{len(to_verify)}] {img_name}")
        print(f"{'='*80}")
        print(f"Prediction:   {prediction}")
        print(f"Ground Truth: {ground_truth}")
        print(f"{'='*80}")
        print("\nLook at the image above.")
        print("Does the prediction match what you SEE in the image?")
        
        response = input("Correct? (y/n/q): ").strip().lower()
        
        plt.close()
        
        if response == 'q':
            print("\nStopping verification...")
            break
        elif response == 'y':
            verified_correct += 1
            print("  ✓ Verified correct")
        elif response == 'n':
            verified_wrong += 1
            print("  ✗ Marked as wrong")
            actual = input("  What text do you actually see? (or press ENTER to skip): ").strip()
            issues.append({
                'image': img_name,
                'prediction': prediction,
                'ground_truth': ground_truth,
                'actual_text': actual if actual else 'Not specified'
            })
        else:
            print("  ? Skipped")
    
    # Summary
    print(f"\n{'='*80}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*80}")
    print(f"Images verified:     {i}")
    print(f"Confirmed correct:   {verified_correct}")
    print(f"Found wrong:         {verified_wrong}")
    
    if verified_wrong > 0:
        print(f"\n⚠️  Issues found:")
        for issue in issues:
            print(f"\n  Image: {issue['image']}")
            print(f"  Prediction:   {issue['prediction']}")
            print(f"  Ground Truth: {issue['ground_truth']}")
            print(f"  Actual Text:  {issue['actual_text']}")
    else:
        print(f"\n✅ All verified predictions match the images!")
    
    # Calculate verified accuracy
    if verified_correct + verified_wrong > 0:
        verified_accuracy = (verified_correct / (verified_correct + verified_wrong) * 100)
        print(f"\nVerified Accuracy: {verified_accuracy:.2f}%")
    
    print(f"{'='*80}")
    
    return verified_correct, verified_wrong, issues


def spot_check_random_samples(results_file, images_dir, n_samples=5):
    """
    Quick spot check of random correct predictions
    """
    import random
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = [r for r in data['detailed_results'] 
               if r.get('correct') and r.get('ground_truth') != 'NO_PATTERN']
    
    if len(results) <= n_samples:
        to_check = results
    else:
        to_check = random.sample(results, n_samples)
    
    print(f"\n{'='*80}")
    print(f"SPOT CHECK: {len(to_check)} Random Correct Predictions")
    print(f"{'='*80}")
    
    verified_correct, verified_wrong, issues = verify_results(
        results_file, images_dir, show_all=False
    )
    
    return verified_correct, verified_wrong


def main():
    results_file = "results/final_submission_results.json"
    images_dir = "data/test_images"
    
    if not Path(results_file).exists():
        print(f"❌ File not found: {results_file}")
        return
    
    print("\n" + "="*80)
    print("RESULTS VERIFICATION TOOL")
    print("="*80)
    print("\nWhat would you like to verify?")
    print("  1. Spot check (5 random correct predictions)")
    print("  2. Verify all correct predictions (20 images)")
    print("  3. Verify ALL results (correct + wrong)")
    
    choice = input("\nChoose (1-3): ").strip()
    
    if choice == '1':
        spot_check_random_samples(results_file, images_dir, n_samples=5)
    elif choice == '2':
        verify_results(results_file, images_dir, show_all=False)
    elif choice == '3':
        verify_results(results_file, images_dir, show_all=True)
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()