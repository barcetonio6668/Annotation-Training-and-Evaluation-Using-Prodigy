import json
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def jsonl_to_xml(jsonl_path, xml_path):
    # Create root element
    root = ET.Element("annotations")
    
    # Read JSONL file
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                # Create annotation element for each record
                annotation = ET.SubElement(root, "annotation")
                
                # Add basic fields
                ET.SubElement(annotation, "text").text = data.get("text", "")
                ET.SubElement(annotation, "answer").text = data.get("answer", "")
                
                # Add tokens if they exist
                if "tokens" in data:
                    tokens_elem = ET.SubElement(annotation, "tokens")
                    for token in data["tokens"]:
                        token_elem = ET.SubElement(tokens_elem, "token")
                        token_elem.set("id", str(token.get("id", "")))
                        token_elem.set("start", str(token.get("start", "")))
                        token_elem.set("end", str(token.get("end", "")))
                        token_elem.text = token.get("text", "")
                
                # Add spans if they exist
                if "spans" in data and data["spans"]:
                    spans_elem = ET.SubElement(annotation, "spans")
                    for span in data["spans"]:
                        span_elem = ET.SubElement(spans_elem, "span")
                        span_elem.set("start", str(span.get("start", "")))
                        span_elem.set("end", str(span.get("end", "")))
                        span_elem.set("label", span.get("label", ""))
                        span_elem.text = span.get("text", "")
                        
                        # Add token references if available
                        if "token_start" in span and "token_end" in span:
                            span_elem.set("token_start", str(span["token_start"]))
                            span_elem.set("token_end", str(span["token_end"]))
                
                # Add metadata
                meta_elem = ET.SubElement(annotation, "metadata")
                ET.SubElement(meta_elem, "input_hash").text = str(data.get("_input_hash", ""))
                ET.SubElement(meta_elem, "task_hash").text = str(data.get("_task_hash", ""))
                ET.SubElement(meta_elem, "timestamp").text = str(data.get("_timestamp", ""))
                ET.SubElement(meta_elem, "view_id").text = data.get("_view_id", "")
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num} in {jsonl_path}: {e}")
    
    # Write prettified XML to file
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(prettify(root))

def convert_directory(input_dir, files_to_convert):
    input_path = Path(input_dir)
    
    for filename in files_to_convert:
        jsonl_file = input_path / filename
        if jsonl_file.exists():
            xml_filename = jsonl_file.stem + '.xml'
            xml_file = input_path / xml_filename
            print(f"Converting {jsonl_file} to {xml_file}")
            jsonl_to_xml(jsonl_file, xml_file)
        else:
            print(f"File not found: {jsonl_file}")

if __name__ == "__main__":
    input_dir = "/Users/liuxduan/Desktop/Prodigy/Checked_Annotations"
    files_to_convert = [
        "annotations_415_Early.jsonl",
        "annotations_449_Latest.jsonl",
        "annotations_1060_Early.jsonl",
        "annotations_1060_Latest.jsonl",
        "annotations_2301_Latest.jsonl"
    ]
    
    convert_directory(input_dir, files_to_convert)
    print("Conversion complete!")