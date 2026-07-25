import json
from pathlib import Path
import csv
import re


def create_review_spreadsheet(jsonl_path, output_csv):
    """
    Create a CSV file for manual review in Excel or Google Sheets
    Uses exact same detection logic as analyze_jsonl_clean.py
    """
    
    # Use exact same patterns as analyze_jsonl_clean.py
    suspicious_patterns = [
        (r'\(\s*[JOI]([a-z])', 'possible OCR: "({letter}" might be something else'),
        (r'([a-z])\s+\(\s*\.', 'possible OCR: "letter (." might be missing text'),
        (r'\{[a-z]\s+\^', 'possible OCR: "{letter} ^" looks suspicious'),
        (r'\\+\s', 'possible OCR: backslash with space'),
        (r'(\d)[l|I]', 'possible OCR: digit followed by l/|/I'),
        (r'[il|I]{3,}', 'possible OCR: multiple l/i/|/I in a row'),
    ]
    
    suspicious_rows = []
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            try:
                data = json.loads(line.strip())
            except:
                continue
            
            text = data.get("text", "")
            
            # Find all suspicious patterns in this text
            found_issues = []
            for pattern, description in suspicious_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    found_issues.append({
                        'matched_text': match.group(0),
                        'position': match.start(),
                        'description': description
                    })
            
            # Add to suspicious rows if any issues found
            if found_issues:
                issue_str = '; '.join([f"{issue['description']}" for issue in found_issues])
                suspicious_rows.append({
                    'line_num': line_num,
                    'text': text,
                    'issue': issue_str,
                    'corrected_text': ''  # Leave blank for manual entry
                })
    
    # Write to CSV
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['line_num', 'text', 'issue', 'corrected_text'])
        writer.writeheader()
        for row in suspicious_rows:
            writer.writerow(row)
    
    print(f"Created review spreadsheet with {len(suspicious_rows)} suspicious lines")
    print(f"Open {output_csv} in Excel or Google Sheets to review and fix")
    
    return suspicious_rows


def batch_create_review_spreadsheets(input_dir):
    """Create review spreadsheets for all cleaned JSONL files"""
    input_path = Path(input_dir)
    
    jsonl_files = [
        "annotations_415_Early.cleaned.jsonl",
        "annotations_449_Latest.cleaned.jsonl",
        "annotations_1060_Early.cleaned.jsonl",
        "annotations_1060_Latest.cleaned.jsonl",
        "annotations_2301_Latest.cleaned.jsonl",
    ]
    
    total_suspicious = 0
    
    for jsonl_name in jsonl_files:
        jsonl_path = input_path / jsonl_name
        output_csv = input_path / (jsonl_name.replace('.jsonl', '.review.csv'))
        
        if jsonl_path.exists():
            print(f"Processing {jsonl_name}...")
            suspicious = create_review_spreadsheet(jsonl_path, output_csv)
            total_suspicious += len(suspicious)
        else:
            print(f"File not found: {jsonl_path}")
    
    print(f"\nTotal suspicious lines across all files: {total_suspicious}")


if __name__ == "__main__":
    input_dir = "/Users/liuxduan/Desktop/Annotation-Training-and-Evaluation-Using-Prodigy-main/Checked_Annotations"
    batch_create_review_spreadsheets(input_dir)
