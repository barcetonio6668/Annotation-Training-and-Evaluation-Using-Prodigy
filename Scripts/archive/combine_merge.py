import os
import re
from lxml import etree
from collections import defaultdict

INPUT_DIR = "/Users/liuxduan/Desktop/Prodigy/Cleaned_Alpine_Journal"
OUTPUT_FILE = os.path.join(INPUT_DIR, "prodigy_annotated.txt")

def load_word_mapping(text_xml):
    """Create word ID to text mapping"""
    tree = etree.parse(text_xml)
    return {
        word.get('id'): word.text 
        for word in tree.xpath('//w')
    }

def extract_entities(ner_xml, word_map):
    """Extract entities and their positions"""
    tree = etree.parse(ner_xml)
    entities = []
    
    # Process geographic entities
    for geo in tree.xpath('//geo/g'):
        span_ids = geo.get('span').split()
        entity_text = ' '.join(word_map[wid] for wid in span_ids if wid in word_map)
        if entity_text:
            entities.append({
                'text': entity_text,
                'type': geo.get('type'),
                'span': geo.get('span')
            })
    
    # Process person entities
    for person in tree.xpath('//persons/person'):
        firstname = person.findtext('firstname', '').strip()
        lastname = person.findtext('lastname', '').strip()
        if firstname or lastname:
            entities.append({
                'text': f"{firstname} {lastname}".strip(),
                'type': 'person',
                'span': None  # Person may not have direct span correspondence
            })
    
    return entities

def reconstruct_text(text_xml):
    """Reconstruct original text"""
    tree = etree.parse(text_xml)
    sentences = []
    
    for s in tree.xpath('//s'):
        sentence = ' '.join(w.text for w in s.xpath('./w'))
        # Simple punctuation normalization
        sentence = re.sub(r'\s([,.!?])', r'\1', sentence)
        sentences.append(sentence)
    
    return ' '.join(sentences)

def process_file_pair(text_file, ner_file, output_handle):
    """Process single file pair"""
    # Load data
    word_map = load_word_mapping(text_file)
    text = reconstruct_text(text_file)
    entities = extract_entities(ner_file, word_map)
    
    # Write output
    base_name = os.path.basename(text_file).replace('_en.xml', '')
    output_handle.write(f"=== {base_name} ===\n")
    output_handle.write(f"{text}\n\n")
    
    if entities:
        output_handle.write("--- Entities ---\n")
        for ent in entities:
            output_handle.write(f"[{ent['text']}|{ent['type'].upper()}]\n")
        output_handle.write("\n")
    
    output_handle.write("="*50 + "\n\n")

def batch_process():
    """Batch process all files"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(INPUT_DIR):
            if filename.endswith('_en.xml'):
                ner_file = filename.replace('_en.xml', '_en-ner.xml')
                ner_path = os.path.join(INPUT_DIR, ner_file)
                
                if os.path.exists(ner_path):
                    try:
                        process_file_pair(
                            os.path.join(INPUT_DIR, filename),
                            ner_path,
                            outfile
                        )
                        print(f"Processed: {filename}")
                    except Exception as e:
                        print(f"Error processing {filename}: {str(e)}")
                else:
                    print(f"Skipping {filename}: No matching NER file")

if __name__ == "__main__":
    batch_process()
    print(f"\nAnnotation complete. Output saved to:\n{OUTPUT_FILE}")