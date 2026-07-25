import csv
import json
from pathlib import Path


def update_jsonl_from_csv(jsonl_path, csv_path, output_jsonl_path):
    """
    Update JSONL file with corrected text from CSV
    
    Args:
        jsonl_path: Original JSONL file
        csv_path: CSV file with corrections
        output_jsonl_path: Output updated JSONL file
    """
    
    # Load corrections from CSV
    corrections = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['corrected_text'].strip():  # Only if correction is not empty
                line_num = int(row['line_num'])
                corrections[line_num] = row['corrected_text']
    
    if not corrections:
        print("No corrections found in CSV")
        return
    
    print(f"Found {len(corrections)} corrections to apply")
    
    # Update JSONL
    updated_count = 0
    with open(jsonl_path, 'r', encoding='utf-8') as f_in, \
         open(output_jsonl_path, 'w', encoding='utf-8') as f_out:
        
        for line_num, line in enumerate(f_in, 1):
            if not line.strip():
                continue
            
            try:
                data = json.loads(line.strip())
            except:
                f_out.write(line)
                continue
            
            # Check if this line has a correction
            if line_num in corrections:
                data['text'] = corrections[line_num]
                updated_count += 1
            
            # Write updated line
            f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    print(f"Updated {updated_count} lines")
    print(f"Saved to: {output_jsonl_path}")


def batch_update_jsonl_files(input_dir):
    """Update all JSONL files with corrections from their CSV files"""
    input_path = Path(input_dir)
    
    file_pairs = [
        ("annotations_415_Early.cleaned.jsonl", "annotations_415_Early.cleaned.review.csv"),
        ("annotations_449_Latest.cleaned.jsonl", "annotations_449_Latest.cleaned.review.csv"),
        ("annotations_1060_Early.cleaned.jsonl", "annotations_1060_Early.cleaned.review.csv"),
        ("annotations_1060_Latest.cleaned.jsonl", "annotations_1060_Latest.cleaned.review.csv"),
        ("annotations_2301_Latest.cleaned.jsonl", "annotations_2301_Latest.cleaned.review.csv"),
    ]
    
    for jsonl_name, csv_name in file_pairs:
        jsonl_path = input_path / jsonl_name
        csv_path = input_path / csv_name
        
        # Output: replace .cleaned.jsonl with .corrected.jsonl
        output_jsonl_path = input_path / jsonl_name.replace('.cleaned.jsonl', '.corrected.jsonl')
        
        if jsonl_path.exists() and csv_path.exists():
            print(f"\nProcessing {jsonl_name}...")
            update_jsonl_from_csv(jsonl_path, csv_path, output_jsonl_path)
        else:
            if not jsonl_path.exists():
                print(f"JSONL file not found: {jsonl_path}")
            if not csv_path.exists():
                print(f"CSV file not found: {csv_path}")


if __name__ == "__main__":
    input_dir = "/Users/liuxduan/Desktop/Annotation-Training-and-Evaluation-Using-Prodigy-main/Checked_Annotations"
    batch_update_jsonl_files(input_dir)
    print("\nAll files updated!")