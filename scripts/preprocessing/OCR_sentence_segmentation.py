import os
import re
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from nltk.tokenize import sent_tokenize
import nltk
from collections import Counter

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")

# Windows users need to set tesseract path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set paths
folder_path = "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022/The Alphine Journal 2022"
output_folder = os.path.join(folder_path, "smart_extracted_sentences")
os.makedirs(output_folder, exist_ok=True)

def clean_text(text):
    """Clean extracted text"""
    # Remove hyphen followed by space (e.g. "self- contained" -> "self-contained")
    text = re.sub(r'-\s+', '-', text)
    
    # Remove hyphens in names (e.g. "Zimmer- man" -> "Zimmerman")
    # Match hyphen pattern in words starting with capital letters
    text = re.sub(r'([A-Z][a-z]+)-\s*([a-z]+)', r'\1\2', text)
    
    # Remove obvious hyphens within words (e.g. "west-ern" -> "western")
    # Match pattern: lowercase-lowercase that are not compound words
    text = re.sub(r'([a-z])-([a-z])', r'\1\2', text)
    
    # Handle obvious single letter splits (conservative approach)
    # Match: single letter + space + single letter + space + letters
    # Example: "h e l l o" but not "a special time"
    text = re.sub(r'\b([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z]+)\b', r'\1\2\3\4\5', text)
    text = re.sub(r'\b([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\b', r'\1\2\3\4', text)
    text = re.sub(r'\b([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\b', r'\1\2\3', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters (keep basic punctuation)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\']+', ' ', text)
    # Remove very short lines (might be page numbers)
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
    return '\n'.join(cleaned_lines)

def is_meaningful_text(text):
    """Check if text is meaningful (not garbage)"""
    if len(text.strip()) < 50:
        return False
    
    # Count letters
    letters = sum(1 for c in text if c.isalpha())
    total_chars = len(text)
    
    # If letter ratio is too low, probably garbage
    if total_chars > 0 and letters / total_chars < 0.5:
        return False
    
    # Check for excessive repeated characters
    char_counts = Counter(text.lower())
    most_common_char_count = char_counts.most_common(1)[0][1] if char_counts else 0
    if most_common_char_count > len(text) * 0.3:  # If one char is >30%
        return False
    
    return True

def extract_text_from_pdf(pdf_path):
    """Extract text using PyMuPDF"""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text.strip():  # Only add non-empty pages
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
    except Exception as e:
        print(f"PyMuPDF extraction failed: {e}")
        return ""
    
    return text.strip()

def ocr_pdf(pdf_path):
    """Extract text using OCR"""
    print(f"Converting PDF {pdf_path} to images for OCR")
    try:
        # Try different DPI settings
        images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=3)  # Test first 3 pages
        if not images:
            return ""
    except Exception as e:
        print(f"PDF to image conversion failed: {e}")
        return ""
    
    text = ""
    for i, image in enumerate(images):
        print(f"OCR processing page {i+1}")
        try:
            # Use better OCR config
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:()[]"\'- '
            page_text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
            if page_text.strip():
                text += f"\n--- Page {i + 1} ---\n"
                text += page_text + "\n"
        except Exception as e:
            print(f"OCR failed on page {i+1}: {e}")
            continue
    
    return text.strip()

def process_sentences(text):
    """Process sentence splitting and cleaning"""
    # Clean text
    cleaned_text = clean_text(text)
    
    # Sentence splitting
    sentences = sent_tokenize(cleaned_text)
    
    # Filter and clean sentences
    processed_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        # Filter too short or too long sentences
        if 10 <= len(sentence) <= 1000:
            # Remove possible header/footer patterns
            if not re.match(r'^(Page \d+|\d+|Chapter \d+)', sentence):
                processed_sentences.append(sentence)
    
    return processed_sentences

def process_pdf_smart(folder_path):
    """Intelligent PDF processing"""
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print("No PDF files found")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for filename in pdf_files:
        pdf_path = os.path.join(folder_path, filename)
        print(f"\nProcessing: {filename}")
        
        # Try standard extraction first
        text = extract_text_from_pdf(pdf_path)
        method = "PyMuPDF"
        
        # Check if OCR is needed
        if not is_meaningful_text(text):
            print("Text extraction failed or poor quality, switching to OCR...")
            text = ocr_pdf(pdf_path)
            method = "OCR"
            
            # If OCR also fails
            if not is_meaningful_text(text):
                print("OCR also failed to extract valid text")
                continue
        
        # Process sentences
        sentences = process_sentences(text)
        
        if not sentences:
            print("No valid sentences extracted")
            continue
        
        # Save results
        output_file = os.path.join(output_folder, filename.replace(".pdf", ".txt"))
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# File: {filename}\n")
                f.write(f"# Extraction method: {method}\n")
                f.write(f"# Sentence count: {len(sentences)}\n\n")
                
                for sentence in sentences:
                    f.write(f"{sentence}\n")
            
            print(f"Successfully extracted {len(sentences)} sentences using {method}, saved to: {output_file}")
            
        except Exception as e:
            print(f"Failed to save file: {e}")

# Run processing
if __name__ == "__main__":
    process_pdf_smart(folder_path)