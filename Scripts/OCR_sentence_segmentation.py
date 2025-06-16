import os
import re
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from nltk.tokenize import sent_tokenize
import nltk
from collections import Counter

# 下载必要的 NLTK 数据
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")

# Windows 用户需要设置 tesseract 路径
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 设置路径
folder_path = "/Users/liuxduan/Desktop/Prodigy/Alphine_Journal_Latest_2020-2022/The Alphine Journal 2022"
output_folder = os.path.join(folder_path, "smart_extracted_sentences")
os.makedirs(output_folder, exist_ok=True)

def clean_text(text):
    """清理提取的文本"""
    # 移除连字符后的空格 (例如 "self- contained" -> "self-contained")
    text = re.sub(r'-\s+', '-', text)
    
    # 移除名字中间的连字符和后面的空格 (例如 "Zimmer- man" -> "Zimmerman")
    # 匹配大写字母开头的单词中的连字符模式
    text = re.sub(r'([A-Z][a-z]+)-\s*([a-z]+)', r'\1\2', text)
    
    # 移除明显是单词内部错误的连字符 (例如 "west-ern" -> "western")
    # 匹配模式：小写字母-连字符-小写字母，且前后都是字母（不是复合词）
    text = re.sub(r'([a-z])-([a-z])', r'\1\2', text)
    
    # 只处理明显的单字母分割模式，更加保守
    # 匹配：单字母 + 空格 + 单字母 + 空格 + 字母，且整体长度较短（可能是被分割的单词）
    # 例如: "h e l l o" 但不影响 "a special time"
    text = re.sub(r'\b([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z]+)\b', r'\1\2\3\4\5', text)
    text = re.sub(r'\b([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\b', r'\1\2\3\4', text)
    text = re.sub(r'\b([a-zA-Z])\s([a-zA-Z])\s([a-zA-Z])\b', r'\1\2\3', text)
    
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符（保留基本标点）
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\']+', ' ', text)
    # 移除过短的"句子"（可能是页码等）
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
    return '\n'.join(cleaned_lines)

def is_meaningful_text(text):
    """判断文本是否有意义（非乱码）"""
    if len(text.strip()) < 50:
        return False
    
    # 统计字母数量
    letters = sum(1 for c in text if c.isalpha())
    total_chars = len(text)
    
    # 如果字母占比太低，可能是乱码
    if total_chars > 0 and letters / total_chars < 0.5:
        return False
    
    # 检查是否有过多重复字符
    char_counts = Counter(text.lower())
    most_common_char_count = char_counts.most_common(1)[0][1] if char_counts else 0
    if most_common_char_count > len(text) * 0.3:  # 如果某个字符占比超过30%
        return False
    
    return True

def extract_text_from_pdf(pdf_path):
    """使用PyMuPDF提取文本"""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text.strip():  # 只添加非空页面
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
    except Exception as e:
        print(f"❌ PyMuPDF 提取失败：{e}")
        return ""
    
    return text.strip()

def ocr_pdf(pdf_path):
    """使用OCR提取文本"""
    print(f"🖼️ OCR 模式：转换 {pdf_path} 为图片")
    try:
        # 尝试不同的DPI设置
        images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=3)  # 先测试前3页
        if not images:
            return ""
    except Exception as e:
        print(f"❌ PDF 转图片失败：{e}")
        return ""
    
    text = ""
    for i, image in enumerate(images):
        print(f"🔍 OCR 第 {i+1} 页")
        try:
            # 使用更好的OCR配置
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:()[]"\'- '
            page_text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
            if page_text.strip():
                text += f"\n--- Page {i + 1} ---\n"
                text += page_text + "\n"
        except Exception as e:
            print(f"⚠️ 第{i+1}页OCR失败：{e}")
            continue
    
    return text.strip()

def process_sentences(text):
    """处理句子分割和清理"""
    # 清理文本
    cleaned_text = clean_text(text)
    
    # 句子分割
    sentences = sent_tokenize(cleaned_text)
    
    # 过滤和清理句子
    processed_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        # 过滤太短或太长的句子
        if 10 <= len(sentence) <= 1000:
            # 移除可能的页眉页脚模式
            if not re.match(r'^(Page \d+|\d+|Chapter \d+)', sentence):
                processed_sentences.append(sentence)
    
    return processed_sentences

def process_pdf_smart(folder_path):
    """智能处理PDF文件夹"""
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print("❌ 未找到PDF文件")
        return
    
    print(f"📚 找到 {len(pdf_files)} 个PDF文件")
    
    for filename in pdf_files:
        pdf_path = os.path.join(folder_path, filename)
        print(f"\n📘 正在处理：{filename}")
        
        # 先尝试普通提取
        text = extract_text_from_pdf(pdf_path)
        method = "PyMuPDF"
        
        # 判断是否需要OCR
        if not is_meaningful_text(text):
            print("⚠️ 文本提取失败或质量差，切换为 OCR...")
            text = ocr_pdf(pdf_path)
            method = "OCR"
            
            # 如果OCR也失败
            if not is_meaningful_text(text):
                print("❌ OCR 也未能提取到有效文本")
                continue
        
        # 处理句子
        sentences = process_sentences(text)
        
        if not sentences:
            print("⚠️ 未提取到有效句子")
            continue
        
        # 保存结果
        output_file = os.path.join(output_folder, filename.replace(".pdf", ".txt"))
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# 文件：{filename}\n")
                f.write(f"# 提取方法：{method}\n")
                f.write(f"# 句子数量：{len(sentences)}\n\n")
                
                for sentence in sentences:
                    f.write(f"{sentence}\n")
            
            print(f"✅ 使用 {method}，提取 {len(sentences)} 个句子，已保存：{output_file}")
            
        except Exception as e:
            print(f"❌ 保存文件失败：{e}")

# 运行处理
if __name__ == "__main__":
    process_pdf_smart(folder_path)