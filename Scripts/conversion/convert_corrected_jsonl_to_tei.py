import json
from pathlib import Path
from xml.dom import minidom


LABEL_TO_TEI = {
    "PERSON": ("name", {"type": "person"}),
    "MOUNTAIN": ("placeName", {"type": "mountain"}),
    "VALLEY": ("placeName", {"type": "valley"}),
    "CITY": ("placeName", {"type": "city"}),
    "GPE": ("placeName", {"type": "gpe"}),
    "DATE": ("date", {}),
}


def escape_xml_text(text):
    """Escape special characters in XML text content"""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def escape_xml_attr(value):
    """Escape special characters in XML attribute values"""
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace('"', "&quot;")
    return value


def attrs_to_string(attrs):
    """Convert attributes dict to XML attribute string"""
    return "".join(
        f' {key}="{escape_xml_attr(value)}"'
        for key, value in attrs.items()
    )


def should_skip_record(text):
    """Skip Prodigy/spaCy helper lines"""
    text = text.strip()

    if not text:
        return True

    if text.startswith("Entities:"):
        return True

    if text.startswith("[") and "|" in text and text.endswith("]"):
        return True

    return False


def insert_spans_into_text(text, spans, verbose=False):
    """
    Insert TEI tags into the original text using Prodigy/spaCy span offsets.
    Only escape where necessary.
    """
    if not spans:
        return escape_xml_text(text)

    # Sort spans by position
    spans = sorted(spans, key=lambda s: (s.get("start", 0), s.get("end", 0)))

    result = []
    last = 0
    errors = []

    for span_idx, span in enumerate(spans):
        start = span.get("start")
        end = span.get("end")
        label = span.get("label", "")

        # Validation
        if start is None or end is None:
            errors.append(f"Span {span_idx}: Missing start/end")
            continue

        if start < 0 or end < 0:
            errors.append(f"Span {span_idx}: Negative index [{start}:{end}]")
            continue

        if start >= end:
            errors.append(f"Span {span_idx}: start >= end [{start}:{end}]")
            continue

        if start > len(text) or end > len(text):
            errors.append(f"Span {span_idx}: Out of range [{start}:{end}], text length={len(text)}")
            continue

        if start < last:
            errors.append(f"Span {span_idx}: Overlaps with previous span (last={last}, start={start})")
            continue

        # Add text before span
        if start > last:
            result.append(escape_xml_text(text[last:start]))

        # Get appropriate TEI tag
        tag, attrs = LABEL_TO_TEI.get(
            label,
            ("name", {"type": label.lower()})
        )

        # Add entity with tags
        entity_text = escape_xml_text(text[start:end])
        attr_string = attrs_to_string(attrs)
        result.append(f"<{tag}{attr_string}>{entity_text}</{tag}>")

        last = end

    # Add remaining text
    if last < len(text):
        result.append(escape_xml_text(text[last:]))

    if errors and verbose:
        for error in errors:
            print(f"  Warning: {error}")

    return "".join(result)


def jsonl_to_tei(jsonl_path, tei_path, verbose=False):
    """Convert JSONL file with NER annotations to TEI XML format"""
    
    body_parts = []
    paragraph_number = 1
    skipped_count = 0
    error_count = 0

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                data = json.loads(line.strip())
            except json.JSONDecodeError as e:
                print(f"Line {line_num}: JSON parse error - {e}")
                error_count += 1
                continue

            text = data.get("text", "")

            if should_skip_record(text):
                skipped_count += 1
                continue

            spans = data.get("spans", [])
            
            try:
                annotated_text = insert_spans_into_text(text, spans, verbose=verbose)
            except Exception as e:
                print(f"Line {line_num}: Processing failed - {e}")
                error_count += 1
                continue

            body_parts.append(
                f'      <p n="{paragraph_number}">{annotated_text}</p>'
            )

            paragraph_number += 1

    title = Path(jsonl_path).stem
    escaped_title = escape_xml_text(title)

    # Build TEI XML
    tei_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>{escaped_title}</title>
      </titleStmt>
      <publicationStmt>
        <p>Generated from Prodigy/spaCy NER annotations.</p>
      </publicationStmt>
      <sourceDesc>
        <p>British Alpine Corpus annotation export.</p>
      </sourceDesc>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
{chr(10).join(body_parts)}
    </body>
  </text>
</TEI>
'''

    # Validate XML structure
    try:
        dom = minidom.parseString(tei_xml)
    except Exception as e:
        print(f"XML validation error: {e}")
        return

    # Write to file
    with open(tei_path, "w", encoding="utf-8") as f:
        f.write(tei_xml)

    print(f"Successfully converted: {paragraph_number - 1} paragraphs, {skipped_count} records skipped, {error_count} errors")


def convert_directory(input_dir, files_to_convert, verbose=False):
    """Convert multiple JSONL files in a directory"""
    input_path = Path(input_dir)

    for filename in files_to_convert:
        jsonl_file = input_path / filename

        if jsonl_file.exists():
            tei_filename = jsonl_file.stem + ".tei.xml"
            tei_file = input_path / tei_filename

            print(f"Converting: {jsonl_file.name} -> {tei_file.name}")
            jsonl_to_tei(jsonl_file, tei_file, verbose=verbose)
        else:
            print(f"File not found: {jsonl_file}")


if __name__ == "__main__":
    input_dir = "/Users/liuxduan/Desktop/Annotation-Training-and-Evaluation-Using-Prodigy-main/Checked_Annotations"

    files_to_convert = [
        "annotations_415_Early.corrected.jsonl",
        "annotations_449_Latest.corrected.jsonl",
        "annotations_1060_Early.corrected.jsonl",
        "annotations_1060_Latest.corrected.jsonl",
        "annotations_2301_Latest.corrected.jsonl"
    ]

    convert_directory(input_dir, files_to_convert, verbose=False)
    print("TEI conversion complete!")