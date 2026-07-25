import os
import re
from lxml import etree
from collections import defaultdict

INPUT_DIR = "/Users/liuxduan/Desktop/Prodigy/Cleaned_Alpine_Journal"
OUTPUT_FILE = os.path.join(INPUT_DIR, "yearly_sentences_annotated.txt")

def load_word_mapping(text_xml):
    """Create word ID to text mapping with sentence context"""
    tree = etree.parse(text_xml)
    word_map = {}
    sentence_map = defaultdict(list)
    
    for s in tree.xpath('//s'):
        s_id = s.get('id')
        for w in s.xpath('./w'):
            word_map[w.get('id')] = (w.text, s_id)
            sentence_map[s_id].append(w.text)
    
    return word_map, sentence_map

def extract_entities(ner_xml, word_map):
    """Extract entities with sentence context"""
    tree = etree.parse(ner_xml)
    entities = []
    
    # Process geographical entities
    for geo in tree.xpath('//geo/g'):
        span_ids = geo.get('span').split()
        entity_words = []
        source_sentences = set()
        
        for wid in span_ids:
            if wid in word_map:
                word, s_id = word_map[wid]
                entity_words.append(word)
                source_sentences.add(s_id)
        
        if entity_words:
            entities.append({
                'text': ' '.join(entity_words),
                'type': geo.get('type'),
                'sentences': list(source_sentences)
            })
    
    # Process person entities
    for person in tree.xpath('//persons/person'):
        firstname = person.findtext('firstname', '').strip()
        lastname = person.findtext('lastname', '').strip()
        if firstname or lastname:
            entities.append({
                'text': f"{firstname} {lastname}".strip(),
                'type': 'person',
                'sentences': []  # Will be matched later
            })
    
    return entities

def reconstruct_sentences(sentence_map):
    """Rebuild sentences with proper formatting"""
    formatted_sentences = []
    for s_id, words in sentence_map.items():
        sentence = ' '.join(words)
        # Fix punctuation spacing
        sentence = re.sub(r'\s([,.!?;:](?:\s|$))', r'\1', sentence)
        sentence = re.sub(r'([(])\s', r'\1', sentence)
        sentence = re.sub(r'\s([)])', r'\1', sentence)
        formatted_sentences.append((s_id, sentence))
    return formatted_sentences

def match_entities_to_sentences(entities, sentence_map):
    """Link entities to their containing sentences"""
    # Convert sentence_map (lists of words) to formatted sentences
    s_id_to_text = {}
    for s_id, words in sentence_map.items():
        sentence = ' '.join(words)
        # Fix punctuation spacing (same as in reconstruct_sentences)
        sentence = re.sub(r'\s([,.!?;:](?:\s|$))', r'\1', sentence)
        sentence = re.sub(r'([(])\s', r'\1', sentence)
        sentence = re.sub(r'\s([)])', r'\1', sentence)
        s_id_to_text[s_id] = sentence
    
    for entity in entities:
        if not entity['sentences']:  # For person entities without direct span
            for s_id, text in s_id_to_text.items():
                if entity['text'] in text:
                    entity['sentences'].append(s_id)
        
        # Convert sentence IDs to sentence texts
        entity['sentence_texts'] = [s_id_to_text[s_id] 
                                   for s_id in entity['sentences'] 
                                   if s_id in s_id_to_text]

def process_year(year_files, output_handle):
    """Process all files for a single year"""
    yearly_sentences = []
    yearly_entities = []
    
    for text_file, ner_file in year_files:
        word_map, sentence_map = load_word_mapping(text_file)
        entities = extract_entities(ner_file, word_map)
        sentences = reconstruct_sentences(sentence_map)
        # Pass the original sentence_map, not the formatted sentences
        match_entities_to_sentences(entities, sentence_map)
        
        yearly_sentences.extend(sentences)
        yearly_entities.extend(entities)
    
    return yearly_sentences, yearly_entities

def format_year_output(year, sentences, entities, output_handle):
    """Format the output for a single year"""
    output_handle.write(f"\n\n=== YEAR {year} ===\n")
    output_handle.write(f"=== Sentences ===\n")
    
    # Group entities by sentence
    sentence_entities = defaultdict(list)
    for ent in entities:
        for s_id in ent['sentences']:
            sentence_entities[s_id].append(ent)
    
    # Write sentences with their entities
    for s_id, sentence in sentences:
        output_handle.write(f"\n{sentence}\n")
        
        if s_id in sentence_entities:
            output_handle.write("  Entities: ")
            output_handle.write(", ".join(
                f"[{e['text']}|{e['type'].upper()}]" 
                for e in sentence_entities[s_id]
            ))
            output_handle.write("\n")
    
    # Write entity index
    output_handle.write(f"\n=== Entity Index ===\n")
    unique_entities = {(e['text'], e['type']) for e in entities}
    for text, type_ in sorted(unique_entities):
        output_handle.write(f"- {text} ({type_.upper()})\n")

def batch_process():
    """Process all files grouped by year"""
    # Group files by year
    year_files = defaultdict(list)
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('_en.xml'):
            year_match = re.search(r'_(\d{4})_', filename)
            if year_match:
                year = year_match.group(1)
                ner_file = filename.replace('_en.xml', '_en-ner.xml')
                ner_path = os.path.join(INPUT_DIR, ner_file)
                
                if os.path.exists(ner_path):
                    year_files[year].append((
                        os.path.join(INPUT_DIR, filename),
                        ner_path
                    ))
    
    # Process each year
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        for year in sorted(year_files.keys()):
            print(f"Processing year {year}...")
            sentences, entities = process_year(year_files[year], outfile)
            format_year_output(year, sentences, entities, outfile)
    
    print(f"\nProcessing complete. Output saved to:\n{OUTPUT_FILE}")

if __name__ == "__main__":
    batch_process()