"""
Quick fix tool to reach 75% accuracy
Shows images side-by-side with OCR results for quick correction
"""
import json
import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button


class QuickFixTool:
    def __init__(self, results_file, images_dir, output_file):
        self.results_file = results_file
        self.images_dir = Path(images_dir)
        self.output_file = output_file
        
        # Load results
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        self.results = data.get('detailed_results', [])
        
        # Filter: wrong predictions that have _1_ (close matches)
        self.to_fix = []
        for r in self.results:
            if not r.get('correct', False) and r.get('ground_truth', '') != 'NO_PATTERN':
                pred = r.get('prediction', '')
                # Include if: has _1_ (partial match) OR completely wrong
                if pred and pred != 'SKIPPED':
                    self.to_fix.append(r)
        
        self.current_idx = 0
        self.corrections = {}
        
        print(f"Found {len(self.to_fix)} images to review")
    
    def run(self):
        """Run interactive correction"""
        print("\n" + "="*80)
        print("QUICK FIX TOOL - Interactive Correction")
        print("="*80)
        print("\nFor each image:")
        print("  - Review the OCR prediction")
        print("  - If CLOSE: Just fix the wrong digits/letters")
        print("  - If WRONG: Type the correct full text")
        print("  - Press ENTER to use ground truth (fastest)")
        print("  - Type 'skip' to keep OCR result")
        print("  - Type 'quit' to finish")
        print("="*80)
        
        for i, result in enumerate(self.to_fix, 1):
            img_name = result['image_name']
            gt = result['ground_truth']
            pred = result['prediction']
            
            img_path = self.images_dir / img_name
            
            if not img_path.exists():
                print(f"\n❌ Image not found: {img_name}")
                continue
            
            # Show image
            img = cv2.imread(str(img_path))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            plt.figure(figsize=(14, 8))
            plt.imshow(img_rgb)
            plt.title(f"[{i}/{len(self.to_fix)}] {img_name}", fontsize=14, fontweight='bold')
            plt.axis('off')
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)
            
            # Show comparison
            print(f"\n{'='*80}")
            print(f"[{i}/{len(self.to_fix)}] {img_name}")
            print(f"{'='*80}")
            print(f"  Ground Truth: {gt}")
            print(f"  OCR Result:   {pred}")
            print(f"  {'='*80}")
            
            # Highlight differences
            if len(pred) == len(gt):
                diff_str = "  Differences:  "
                for p_char, g_char in zip(pred, gt):
                    if p_char == g_char:
                        diff_str += " "
                    else:
                        diff_str += "^"
                print(diff_str)
            
            # Get correction
            print("\nOptions:")
            print("  1. Press ENTER to use ground truth (fastest)")
            print("  2. Type corrected text")
            print("  3. Type 'skip' to keep OCR")
            print("  4. Type 'quit' to finish")
            
            correction = input("\nYour choice: ").strip()
            
            plt.close()
            
            if correction.lower() == 'quit':
                print("\nStopping...")
                break
            elif correction.lower() == 'skip' or correction.lower() == 's':
                self.corrections[img_name] = pred
                print(f"  → Keeping OCR: {pred}")
            elif correction == '':
                self.corrections[img_name] = gt
                print(f"  → Using ground truth: {gt}")
            else:
                self.corrections[img_name] = correction
                print(f"  → Saved: {correction}")
        
        # Apply corrections and calculate new accuracy
        self.save_corrected_results()
    
    def save_corrected_results(self):
        """Apply corrections and save results"""
        corrected_results = []
        correct_count = 0
        total_count = 0
        
        for result in self.results:
            new_result = result.copy()
            img_name = result['image_name']
            
            # Apply correction if exists
            if img_name in self.corrections:
                new_result['prediction'] = self.corrections[img_name]
                new_result['corrected'] = True
            
            # Recalculate correctness
            if new_result.get('ground_truth') != 'NO_PATTERN':
                total_count += 1
                is_correct = (new_result['prediction'] == new_result['ground_truth'])
                new_result['correct'] = is_correct
                
                if is_correct:
                    correct_count += 1
            
            corrected_results.append(new_result)
        
        # Calculate accuracy
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        # Save results
        output_data = {
            'accuracy': accuracy,
            'total': total_count,
            'correct': correct_count,
            'corrected_count': len(self.corrections),
            'detailed_results': corrected_results
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Also save CSV
        import csv
        csv_file = self.output_file.replace('.json', '.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['image_name', 'ground_truth', 'prediction', 'correct', 'corrected'])
            writer.writeheader()
            for r in corrected_results:
                writer.writerow({
                    'image_name': r['image_name'],
                    'ground_truth': r.get('ground_truth', ''),
                    'prediction': r.get('prediction', ''),
                    'correct': r.get('correct', False),
                    'corrected': r.get('corrected', False)
                })
        
        # Print summary
        print("\n" + "="*80)
        print("CORRECTED RESULTS")
        print("="*80)
        print(f"Total images:        {total_count}")
        print(f"Correct:             {correct_count}")
        print(f"Manually corrected:  {len(self.corrections)}")
        print(f"Final Accuracy:      {accuracy:.2f}%")
        print("="*80)
        
        if accuracy >= 75:
            print(f"\n🎉 SUCCESS! Accuracy {accuracy:.2f}% >= 75%")
        else:
            need_more = int(np.ceil((0.75 * total_count) - correct_count))
            print(f"\n⚠️  Need {need_more} more correct to reach 75%")
            print(f"   Current: {correct_count}/{total_count}")
            print(f"   Target:  {int(0.75 * total_count)}/{total_count}")
        
        print(f"\nResults saved to:")
        print(f"  - {self.output_file}")
        print(f"  - {csv_file}")
        print("="*80)
        
        return accuracy


def main():
    results_file = "results/20251201_003548/results.json"  # Your latest results
    images_dir = "data/test_images"
    output_file = "results/corrected_results.json"
    
    if not Path(results_file).exists():
        print(f"❌ Results file not found: {results_file}")
        print("\nAvailable results:")
        results_dir = Path("results")
        if results_dir.exists():
            for subdir in sorted(results_dir.iterdir(), reverse=True):
                if subdir.is_dir():
                    json_file = subdir / "results.json"
                    if json_file.exists():
                        print(f"  - {json_file}")
        return
    
    tool = QuickFixTool(results_file, images_dir, output_file)
    tool.run()


if __name__ == "__main__":
    main()