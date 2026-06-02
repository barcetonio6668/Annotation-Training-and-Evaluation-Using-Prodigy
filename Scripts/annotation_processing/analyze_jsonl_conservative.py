import json
from pathlib import Path
import re


# Only clean up definite encoding/control character issues
CHAR_REPLACEMENTS = {
    '\u00a0': ' ',      # Non-breaking space -> regular space
    '\u00ad': '',       # Soft hyphen -> remove
}

# Remove all control characters (0x00-0x1F)
CHARS_TO_REMOVE = [chr(i) for i in range(0x00, 0x20)]


def clean_text(text):
    """Clean text conservatively - only remove control characters and encoding issues"""
    if not text:
        return text
    
    # Replace known encoding error characters
    for old_char, new_char in CHAR_REPLACEMENTS.items():
        text = text.replace(old_char, new_char)
    
    # Remove control characters
    for char in CHARS_TO_REMOVE:
        text = text.replace(char, '')
    
    return text


def find_suspicious_patterns(text):
    """Find possible OCR errors but don't auto-fix"""
    issues = []
    
    # Find possible OCR error patterns
    patterns = [
        (r'\(\s*[JOI]([a-z])', 'possible OCR: "({letter}" might be something else'),
        (r'([a-z])\s+\(\s*\.', 'possible OCR: "letter (." might be missing text'),
        (r'\{[a-z]\s+\^', 'possible OCR: "{letter} ^" looks suspicious'),
        (r'\\+\s', 'possible OCR: backslash with space'),
        (r'(\d)[l|I]', 'possible OCR: digit followed by l/|/I'),
        (r'[il|I]{3,}', 'possible OCR: multiple l/i/|/I in a row'),
    ]
    
    for pattern, description in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            issues.append({
                'text': match.group(0),
                'position': match.start(),
                'description': description
            })
    
    return issues


def analyze_jsonl_file(input_path, output_path, report_path=None, find_issues=True):
    """Analyze and clean JSONL file"""
    
    lines_processed = 0
    lines_cleaned = 0
    suspicious_lines = []
    
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        
        for line_num, line in enumerate(f_in, 1):
            if not line.strip():
                continue
            
            try:
                data = json.loads(line.strip())
            except json.JSONDecodeError as e:
                print(f"Line {line_num}: Cannot parse JSON - {e}")
                continue
            
            lines_processed += 1
            original_text = data.get("text", "")
            
            # Clean encoding issues and control characters
            cleaned_text = clean_text(original_text)
            
            if cleaned_text != original_text:
                lines_cleaned += 1
                data["text"] = cleaned_text
            
            # Find possible OCR errors (but don't fix)
            if find_issues:
                issues = find_suspicious_patterns(cleaned_text)
                if issues:
                    suspicious_lines.append({
                        'line_num': line_num,
                        'text': cleaned_text[:120],
                        'issues': issues
                    })
            
            # Write output data
            f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    # Generate report
    print(f"Analysis complete!")
    print(f"  Lines processed: {lines_processed}")
    if lines_cleaned > 0:
        print(f"  Lines cleaned (control characters): {lines_cleaned}")
    else:
        print(f"  No control characters found")
    print(f"  Suspicious lines (possible OCR issues): {len(suspicious_lines)}")
    
    if report_path:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("JSONL Analysis Report\n")
            f.write("=" * 100 + "\n\n")
            f.write(f"Lines processed: {lines_processed}\n")
            if lines_cleaned > 0:
                f.write(f"Lines cleaned (control characters): {lines_cleaned}\n")
            else:
                f.write(f"No control characters found\n")
            f.write(f"Suspicious lines found: {len(suspicious_lines)}\n")
            f.write("\n" + "=" * 100 + "\n")
            f.write("SUSPICIOUS LINES (Need manual review):\n")
            f.write("=" * 100 + "\n\n")
            
            for item in suspicious_lines[:100]:
                f.write(f"\nLine {item['line_num']}\n")
                f.write(f"Text: {item['text']}\n")
                f.write(f"Issues found:\n")
                for issue in item['issues']:
                    f.write(f"  - Position {issue['position']}: '{issue['text']}' -> {issue['description']}\n")
            
            if len(suspicious_lines) > 100:
                f.write(f"\n... and {len(suspicious_lines) - 100} more suspicious lines\n")
        
        print(f"  Report saved to: {report_path}")


def batch_analyze_directory(input_dir, files_to_analyze):
    """Batch analyze multiple JSONL files"""
    input_path = Path(input_dir)
    
    for filename in files_to_analyze:
        jsonl_file = input_path / filename
        
        if not jsonl_file.exists():
            print(f"File not found: {jsonl_file}")
            continue
        
        cleaned_file = input_path / (jsonl_file.stem + ".cleaned.jsonl")
        report_file = input_path / (jsonl_file.stem + ".analysis.txt")
        
        print(f"Analyzing: {filename}")
        analyze_jsonl_file(jsonl_file, cleaned_file, report_file, find_issues=True)
        print(f"  Cleaned file: {cleaned_file.name}")
        print(f"  Report file: {report_file.name}")


if __name__ == "__main__":
    input_dir = "/Users/liuxduan/Desktop/Annotation-Training-and-Evaluation-Using-Prodigy-main/Checked_Annotations"
    
    files_to_analyze = [
        "annotations_415_Early.jsonl",
        "annotations_449_Latest.jsonl",
        "annotations_1060_Early.jsonl",
        "annotations_1060_Latest.jsonl",
        "annotations_2301_Latest.jsonl"
    ]
    
    batch_analyze_directory(input_dir, files_to_analyze)
    print("Analysis complete!")