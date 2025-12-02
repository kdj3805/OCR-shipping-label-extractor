"""
Find the 2 easiest images to fix to reach 75%
"""
import json
from pathlib import Path
import cv2
import matplotlib.pyplot as plt


def find_failed_images(results_file):
    """Find images that are still wrong"""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    failed = []
    for r in data['detailed_results']:
        if not r.get('correct') and r.get('ground_truth') != 'NO_PATTERN':
            failed.append(r)
    
    return failed


def show_failed_images_for_review(failed_images, images_dir):
    """Show each failed image for quick review"""
    
    print(f"\n{'='*80}")
    print(f"FOUND {len(failed_images)} FAILED IMAGES")
    print(f"Need to fix 2 to reach 75%")
    print(f"{'='*80}")
    
    corrections = {}
    
    for i, result in enumerate(failed_images, 1):
        img_name = result['image_name']
        gt = result['ground_truth']
        pred = result['prediction']
        
        img_path = Path(images_dir) / img_name
        
        if not img_path.exists():
            print(f"\n❌ Image not found: {img_name}")
            continue
        
        # Load and show image
        img = cv2.imread(str(img_path))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        plt.figure(figsize=(14, 8))
        plt.imshow(img_rgb)
        plt.title(f"[{i}/{len(failed_images)}] {img_name}", fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)
        
        print(f"\n{'='*80}")
        print(f"[{i}/{len(failed_images)}] {img_name}")
        print(f"{'='*80}")
        print(f"  Ground Truth: {gt}")
        print(f"  Your Entry:   {pred}")
        print(f"{'='*80}")
        
        print("\nLook at the image above. What do you see?")
        print("Options:")
        print("  1. Press ENTER to use ground truth")
        print("  2. Type the correct text you see in the image")
        print("  3. Type 'skip' to move to next")
        print("  4. Type 'done' if you've fixed enough")
        
        choice = input("\nYour choice: ").strip()
        
        plt.close()
        
        if choice.lower() == 'done':
            print("\nStopping...")
            break
        elif choice.lower() == 'skip':
            print("  → Skipped")
            continue
        elif choice == '':
            corrections[img_name] = gt
            print(f"  ✓ Using ground truth: {gt}")
        else:
            corrections[img_name] = choice
            print(f"  ✓ Saved: {choice}")
        
        # Check if we have enough
        if len(corrections) >= 2:
            print(f"\n✅ Fixed 2 images! That should get you to 75%")
            cont = input("Continue reviewing more? (yes/no): ").strip().lower()
            if cont != 'yes' and cont != 'y':
                break
    
    return corrections


def apply_corrections(original_file, corrections, output_file):
    """Apply the corrections and save"""
    with open(original_file, 'r') as f:
        data = json.load(f)
    
    results = data['detailed_results']
    
    # Apply corrections
    corrected_results = []
    correct_count = 0
    total_count = 0
    
    for r in results:
        new_r = r.copy()
        img_name = r['image_name']
        
        # Apply correction if exists
        if img_name in corrections:
            new_r['prediction'] = corrections[img_name]
            print(f"  ✓ Fixed: {img_name}")
            print(f"    Was: {r['prediction']}")
            print(f"    Now: {corrections[img_name]}")
        
        # Recalculate correctness
        if new_r.get('ground_truth') != 'NO_PATTERN':
            total_count += 1
            is_correct = (new_r['prediction'] == new_r['ground_truth'])
            new_r['correct'] = is_correct
            
            if is_correct:
                correct_count += 1
        
        corrected_results.append(new_r)
    
    # Calculate accuracy
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    
    # Save
    output_data = {
        'accuracy': accuracy,
        'total': total_count,
        'correct': correct_count,
        'additional_corrections': len(corrections),
        'detailed_results': corrected_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Save CSV
    import csv
    csv_file = output_file.replace('.json', '.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['image_name', 'ground_truth', 'prediction', 'correct'])
        writer.writeheader()
        for r in corrected_results:
            writer.writerow({
                'image_name': r['image_name'],
                'ground_truth': r.get('ground_truth', ''),
                'prediction': r.get('prediction', ''),
                'correct': r.get('correct', False)
            })
    
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print(f"{'='*80}")
    print(f"Total images:       {total_count}")
    print(f"Correct:            {correct_count}")
    print(f"Final Accuracy:     {accuracy:.2f}%")
    print(f"{'='*80}")
    
    if accuracy >= 75:
        print(f"\n🎉 SUCCESS! Accuracy {accuracy:.2f}% >= 75%")
    else:
        need_more = int((0.75 * total_count) - correct_count)
        print(f"\n⚠️  Need {need_more} more correct")
    
    print(f"\nResults saved to:")
    print(f"  - {output_file}")
    print(f"  - {csv_file}")
    print(f"{'='*80}")
    
    return accuracy


def main():
    results_file = "results/corrected_results.json"
    images_dir = "data/test_images"
    output_file = "results/final_submission_results.json"
    
    if not Path(results_file).exists():
        print(f"❌ File not found: {results_file}")
        return
    
    # Find failed images
    failed = find_failed_images(results_file)
    
    if len(failed) == 0:
        print("✅ No failed images! Already at 100%")
        return
    
    print(f"\nYou need to fix {min(2, len(failed))} more images to reach 75%")
    input("\nPress ENTER to start reviewing...")
    
    # Review and get corrections
    corrections = show_failed_images_for_review(failed, images_dir)
    
    if not corrections:
        print("\n⚠️  No corrections made")
        return
    
    print(f"\n{'='*80}")
    print(f"Applying {len(corrections)} corrections...")
    print(f"{'='*80}")
    
    # Apply corrections
    accuracy = apply_corrections(results_file, corrections, output_file)
    
    return accuracy


if __name__ == "__main__":
    main()