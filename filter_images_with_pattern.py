"""
Utility script to filter and organize images based on whether they have _1_ pattern
"""
import os
import shutil
import csv
import json


def separate_images_by_pattern(ground_truth_csv):
    """
    Separate images into those with and without _1_ pattern
    """
    with_pattern = []
    without_pattern = []
    
    with open(ground_truth_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ground_truth'] == 'NO_PATTERN':
                without_pattern.append(row['image_name'])
            else:
                with_pattern.append(row['image_name'])
    
    return with_pattern, without_pattern


def create_filtered_ground_truth(input_csv, output_csv):
    """
    Create a new ground truth CSV excluding NO_PATTERN images
    """
    filtered_data = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ground_truth'] != 'NO_PATTERN':
                filtered_data.append(row)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['image_name', 'ground_truth'])
        writer.writeheader()
        writer.writerows(filtered_data)
    
    return len(filtered_data)


def organize_images_into_folders(images_dir, ground_truth_csv):
    """
    Organize images into separate folders based on pattern presence
    """
    # Create folders
    with_pattern_dir = os.path.join(os.path.dirname(images_dir), 'images_with_pattern')
    without_pattern_dir = os.path.join(os.path.dirname(images_dir), 'images_without_pattern')
    
    os.makedirs(with_pattern_dir, exist_ok=True)
    os.makedirs(without_pattern_dir, exist_ok=True)
    
    with_pattern, without_pattern = separate_images_by_pattern(ground_truth_csv)
    
    # Copy images
    print("\nOrganizing images...")
    
    for img in with_pattern:
        src = os.path.join(images_dir, img)
        dst = os.path.join(with_pattern_dir, img)
        if os.path.exists(src):
            shutil.copy2(src, dst)
    
    for img in without_pattern:
        src = os.path.join(images_dir, img)
        dst = os.path.join(without_pattern_dir, img)
        if os.path.exists(src):
            shutil.copy2(src, dst)
    
    print(f"✓ Copied {len(with_pattern)} images WITH pattern to: {with_pattern_dir}")
    print(f"✓ Copied {len(without_pattern)} images WITHOUT pattern to: {without_pattern_dir}")


def print_summary(ground_truth_csv):
    """
    Print summary of ground truth data
    """
    with_pattern = 0
    without_pattern = 0
    
    with open(ground_truth_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ground_truth'] == 'NO_PATTERN':
                without_pattern += 1
            else:
                with_pattern += 1
    
    total = with_pattern + without_pattern
    
    print("\n" + "=" * 80)
    print("GROUND TRUTH SUMMARY")
    print("=" * 80)
    print(f"Total images: {total}")
    print(f"Images WITH '_1_' pattern: {with_pattern} ({with_pattern/total*100:.1f}%)")
    print(f"Images WITHOUT pattern: {without_pattern} ({without_pattern/total*100:.1f}%)")
    print("=" * 80)
    
    if without_pattern > 0:
        print("\n⚠️  Note: Images without pattern will be excluded from accuracy calculation")
        print("   They are marked as 'NO_PATTERN' in the CSV")


if __name__ == "__main__":
    ground_truth_csv = "data/ground_truth.csv"
    images_dir = "data/test_images"
    
    if not os.path.exists(ground_truth_csv):
        print(f"❌ Error: {ground_truth_csv} not found!")
        print("   Run create_ground_truth.py first")
        exit(1)
    
    # Print summary
    print_summary(ground_truth_csv)
    
    print("\n" + "=" * 80)
    print("AVAILABLE ACTIONS")
    print("=" * 80)
    print("\n1. Create filtered ground truth (only images with pattern)")
    print("2. Organize images into separate folders")
    print("3. Both")
    print("4. Exit")
    
    choice = input("\nChoose action (1-4): ").strip()
    
    if choice == '1' or choice == '3':
        output_csv = "data/ground_truth_filtered.csv"
        count = create_filtered_ground_truth(ground_truth_csv, output_csv)
        print(f"\n✅ Created filtered ground truth: {output_csv}")
        print(f"   Contains {count} images with '_1_' pattern")
        print("\nUse this for testing:")
        print(f"   python test_batch.py --input_dir data/test_images --ground_truth {output_csv}")
    
    if choice == '2' or choice == '3':
        organize_images_into_folders(images_dir, ground_truth_csv)
        print("\n✅ Images organized into folders")
        print("\nYou can now test only images with pattern:")
        print("   python test_batch.py --input_dir data/images_with_pattern --ground_truth data/ground_truth_filtered.csv")
    
    if choice == '4':
        print("Exiting...")
    
    print("\n" + "=" * 80)