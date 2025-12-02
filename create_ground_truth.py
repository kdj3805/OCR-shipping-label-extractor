"""
Generate ground truth - Manual entry required
Since filenames only contain partial pattern (number_1), 
we need to manually view and enter the complete text from images
"""
import os
import csv
import json
from PIL import Image
import matplotlib.pyplot as plt


def extract_image_id_from_filename(filename):
    """
    Extract just the image identifier from filename
    reverseWaybill-156387426414724544_1.jpg -> 156387426414724544_1
    """
    # Remove extension
    name_without_ext = os.path.splitext(filename)[0]
    
    # Extract the number_1 part after reverseWaybill-
    if 'reverseWaybill-' in name_without_ext:
        return name_without_ext.replace('reverseWaybill-', '')
    
    return name_without_ext


def create_manual_ground_truth(images_dir, output_csv):
    """
    Create ground truth by manually viewing images and entering text
    Since your filenames are like: reverseWaybill-NUMBER_1.jpg
    But the actual text in image is: NUMBER_1_TEXT
    """
    print("=" * 80)
    print("MANUAL GROUND TRUTH GENERATION")
    print("=" * 80)
    print("\nYour image filenames only contain partial pattern (NUMBER_1)")
    print("We need to view each image and enter the COMPLETE text (NUMBER_1_TEXT)")
    print("\nInstructions:")
    print("  - An image will be displayed")
    print("  - Look for text containing '_1_' pattern")
    print("  - Enter the COMPLETE text (e.g., 163233702292313922_1_lWV)")
    print("  - Type 'none' if the image has NO '_1_' pattern")
    print("  - Press Enter to skip (won't be included)")
    print("  - Type 'quit' to exit")
    print("=" * 80)
    
    # Get all image files
    image_files = []
    for file in os.listdir(images_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_files.append(file)
    
    image_files.sort()
    
    print(f"\nFound {len(image_files)} images")
    input("\nPress Enter to start...")
    
    ground_truth_data = []
    
    for i, img_file in enumerate(image_files, 1):
        img_path = os.path.join(images_dir, img_file)
        
        try:
            # Display image
            img = Image.open(img_path)
            plt.figure(figsize=(12, 10))
            plt.imshow(img)
            plt.title(f"Image {i}/{len(image_files)}: {img_file}", fontsize=14, fontweight='bold')
            plt.axis('off')
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)
            
            # Get input
            print(f"\n{'=' * 80}")
            print(f"Image {i}/{len(image_files)}: {img_file}")
            print(f"{'=' * 80}")
            
            # Extract the number_1 part from filename as a hint
            file_hint = extract_image_id_from_filename(img_file)
            print(f"Hint from filename: {file_hint}")
            print(f"\nLook for text in the image that contains '_1_'")
            print(f"Expected format: NUMBERS_1_LETTERS (e.g., {file_hint}_ABC)")
            
            text = input("\nEnter the COMPLETE text containing '_1_' (or type 'none' if no pattern exists): ").strip()
            
            plt.close()
            
            if text.lower() == 'quit':
                print("\nStopping...")
                break
            
            if text.lower() == 'none' or text.lower() == 'n/a' or text.lower() == 'skip':
                # Mark as having no pattern
                ground_truth_data.append({
                    'image_name': img_file,
                    'ground_truth': 'NO_PATTERN'
                })
                print(f"✓ Marked as NO_PATTERN")
            elif text:
                ground_truth_data.append({
                    'image_name': img_file,
                    'ground_truth': text
                })
                print(f"✓ Saved: {text}")
            else:
                print("⊘ Skipped (will not be included in accuracy calculation)")
        
        except Exception as e:
            print(f"Error processing {img_file}: {e}")
            plt.close()
            continue
    
    print("\n" + "=" * 80)
    
    # Save to CSV
    if ground_truth_data:
        # Create output directory
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['image_name', 'ground_truth'])
            writer.writeheader()
            writer.writerows(ground_truth_data)
        
        print(f"\n✅ Ground truth saved to: {output_csv}")
        print(f"   Total entries: {len(ground_truth_data)}")
        
        # Also save as JSON
        json_output = output_csv.replace('.csv', '.json')
        json_data = {item['image_name']: item['ground_truth'] for item in ground_truth_data}
        
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"   Also saved as: {json_output}")
        
        # Show summary
        print("\n" + "=" * 80)
        print("SUMMARY OF COLLECTED DATA:")
        print("=" * 80)
        for item in ground_truth_data[:10]:  # Show first 10
            print(f"  {item['image_name']:<45} -> {item['ground_truth']}")
        if len(ground_truth_data) > 10:
            print(f"  ... and {len(ground_truth_data) - 10} more entries")
    else:
        print("\n⚠️  No ground truth data collected!")
    
    return ground_truth_data


def create_automatic_ground_truth_with_ocr(images_dir, output_csv):
    """
    Alternative: Use OCR to extract ground truth automatically
    This will process all images and extract text containing '_1_'
    """
    print("=" * 80)
    print("AUTOMATIC GROUND TRUTH GENERATION USING OCR")
    print("=" * 80)
    print("\nThis will process all images with OCR to extract ground truth.")
    print("This may take several minutes...")
    
    proceed = input("\nProceed with automatic OCR extraction? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Cancelled.")
        return []
    
    # Import OCR components
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from preprocessing import ImagePreprocessor
        from ocr_engine import OCREngine
        from text_extraction import TextExtractor
    except ImportError as e:
        print(f"\n❌ Error importing OCR modules: {e}")
        print("Make sure all source files are in the 'src' directory.")
        return []
    
    # Get all image files
    image_files = []
    for file in os.listdir(images_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_files.append(file)
    
    image_files.sort()
    print(f"\nFound {len(image_files)} images")
    
    # Initialize OCR components
    print("\nInitializing OCR engines...")
    preprocessor = ImagePreprocessor()
    ocr_engine = OCREngine()
    extractor = TextExtractor()
    
    ground_truth_data = []
    successful = 0
    failed = 0
    
    print("\nProcessing images...")
    print("-" * 80)
    
    for i, img_file in enumerate(image_files, 1):
        img_path = os.path.join(images_dir, img_file)
        
        try:
            print(f"[{i}/{len(image_files)}] Processing {img_file}...", end=' ')
            
            # Preprocess
            preprocessed_images, _ = preprocessor.preprocess_pipeline(img_path)
            
            if preprocessed_images is None:
                print("✗ Preprocessing failed")
                failed += 1
                continue
            
            # OCR
            ocr_results = ocr_engine.combined_ocr(preprocessed_images)
            
            # Extract target
            target_text = extractor.extract_best_match(ocr_results)
            
            if target_text:
                target_text = extractor.post_process_result(target_text)
                ground_truth_data.append({
                    'image_name': img_file,
                    'ground_truth': target_text
                })
                print(f"✓ {target_text}")
                successful += 1
            else:
                print("✗ No pattern found")
                failed += 1
        
        except Exception as e:
            print(f"✗ Error: {e}")
            failed += 1
    
    print("-" * 80)
    print(f"\nSummary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(image_files)}")
    
    # Save results
    if ground_truth_data:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['image_name', 'ground_truth'])
            writer.writeheader()
            writer.writerows(ground_truth_data)
        
        print(f"\n✅ Ground truth saved to: {output_csv}")
        print(f"   Total entries: {len(ground_truth_data)}")
        
        # Also save as JSON
        json_output = output_csv.replace('.csv', '.json')
        json_data = {item['image_name']: item['ground_truth'] for item in ground_truth_data}
        
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"   Also saved as: {json_output}")
    
    return ground_truth_data


if __name__ == "__main__":
    images_dir = "data/test_images"
    output_csv = "data/ground_truth.csv"
    
    # Check if directory exists
    if not os.path.exists(images_dir):
        print(f"❌ Error: Directory '{images_dir}' not found!")
        print(f"   Please create it and add your images.")
        exit(1)
    
    # Check if there are any images
    image_count = len([f for f in os.listdir(images_dir) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
    
    if image_count == 0:
        print(f"❌ Error: No images found in '{images_dir}'!")
        exit(1)
    
    print("\n" + "=" * 80)
    print("GROUND TRUTH GENERATION OPTIONS")
    print("=" * 80)
    print("\n1. Manual Entry - View each image and type the text")
    print("   Pros: Most accurate, you control the data")
    print("   Cons: Takes time for many images")
    print("\n2. Automatic OCR - Use OCR to extract text automatically")
    print("   Pros: Fast, no manual work")
    print("   Cons: May have errors, needs verification")
    print("\n" + "=" * 80)
    
    choice = input("\nChoose method (1 or 2): ").strip()
    
    if choice == '1':
        ground_truth_data = create_manual_ground_truth(images_dir, output_csv)
    elif choice == '2':
        ground_truth_data = create_automatic_ground_truth_with_ocr(images_dir, output_csv)
    else:
        print("Invalid choice. Exiting.")
        exit(1)
    
    if ground_truth_data:
        print("\n" + "=" * 80)
        print("✅ GROUND TRUTH GENERATION COMPLETE!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Review the generated ground_truth.csv file")
        print("  2. Run Streamlit app: streamlit run app.py")
        print("  3. Run batch testing:")
        print("     python test_batch.py --input_dir data/test_images --ground_truth data/ground_truth.csv")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("⚠️  NO GROUND TRUTH DATA GENERATED")
        print("=" * 80)
        print("\nYou can still:")
        print("  1. Test individual images in Streamlit app: streamlit run app.py")
        print("  2. Run batch processing without accuracy calculation:")
        print("     python test_batch.py --input_dir data/test_images")
        print("=" * 80)