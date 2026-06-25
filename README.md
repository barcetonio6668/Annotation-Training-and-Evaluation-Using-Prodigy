# 🏔️ Named Entity Recognition with Prodigy — Alpine Journal Project

This project uses [Prodigy](https://prodi.gy/) for annotating and training a custom Named Entity Recognition (NER) model on texts from the **British Alpine Journal (mainly 2020–2022)**. The goal is to identify and extract six domain-specific entity types: PERSON, MOUNTAIN, VALLEY, CITY, GPE, and DATE. The TEI exports are derived from the corrected JSONL annotations and are intended for publication, preservation, and interoperability purposes. TEI exports were checked for common conversion issues, including residual annotation helper text, malformed XML entities, and unconverted annotation tags. Validation did not identify any such issues in the final TEI files.

## Corpus Preparation Scripts

The repository also contains scripts used during corpus preparation and exploratory analysis:

* `OCR_sentence_segmentation.py` – Segments OCR-derived Alpine Journal texts into sentence-level units suitable for annotation.
* `merge_txt.py` - Merges extracted sentence files from multiple Alpine Journal volumes into a single annotation-ready text file.
* `yearly_sentences_annotated.py` – Generates year-based sentence files with linked named entities for corpus inspection and annotation review.

# 🚀 Annotation Workflow Summary

## 1️⃣ Activate the Virtual Environment

```bash
cd /path/to/project-folder
source venv/bin/activate
```

## 2️⃣ Start Annotation Interface

```bash
prodigy ner.correct golden_standard_dataset en_core_web_sm "path/to/your/annotation/data.txt" --label PERSON,MOUNTAIN,VALLEY,CITY,GPE,DATE
```

This will launch Prodigy at http://localhost:8080.
- `en_core_web_sm` is a base model from SpaCy for English
- When you're done annotating, press Ctrl+C in the terminal to safely exit and save your work.

## 3️⃣ Export the Annotations (JSONL format)

If you have not configured anything specifically, Prodigy defaults to using an SQLite database located in your working directory, at the following path:

```
.prodigy/prodigy.db
```

**Saving Command:**

```bash
prodigy db-out your_dataset_name > annotations.jsonl
```

## 4️⃣ Train a Custom NER Model with Prodigy

```bash
prodigy train model_name_of_your_choice --ner golden_standard_dataset --base-model path_to_your_baseline_model
```

## 5️⃣ Use the Trained Model (Inference Example)

```python
import spacy

nlp = spacy.load("ner-model/model-best")
doc = nlp("John Smith climbed Mount Everest in 2021.")  # Your example sentence
for ent in doc.ents:
    print(ent.text, ent.label_)
```

## Processing Stages

1. **Original annotations (`*.jsonl`)**

   * Direct exports from Prodigy.
   * Used as the primary annotation source.

2. **Cleaned annotations (`*.cleaned.jsonl`) and Analysis reports (`*.analysis.txt`)**

   * Automatically cleaned versions of the original annotations.
   * Annotation analysis and validation reports generated during the review process.
   * Generated using:

     * `analyze_jsonl_conservative.py` 

3. **Review files (`*.cleaned.review.csv`)**

   * Spreadsheet files generated for manual inspection and correction.
   * Generated using:

     * `create_review_spreadsheet.py`
    
4. **Corrected annotations (`*.corrected.jsonl`)**

   * After manually reviewing and correcting annotation files.
   * Updated using:

     * `update_jsonl_from_csv.py`
     * Output files serve as the final gold-standard annotation dataset.

5. **XML exports (`*.xml`, `*.corrected.xml`)**

   * Structured XML representations preserving annotation metadata, tokenisation, and span information.
   * Generated using:

     * `convert_corrected_jsonl_to_xml.py`

6. **TEI exports (`*.corrected.tei.xml`)**

   * TEI-compatible XML versions generated from the corrected annotations.
   * Intended for corpus publication, interoperability, and digital humanities applications.
   * Generated using:

     * `convert_corrected_jsonl_to_tei.py`

The corrected JSONL files remain the authoritative annotation source used for model development and evaluation.

## 📁 Repository Structure

```text
Scripts/
├── post-manual_check/
│   ├── analyze_jsonl_conservative.py
│   ├── create_review_spreadsheet.py
│   └── update_jsonl_from_csv.py
├── conversion/
│   ├── convert_corrected_jsonl_to_xml.py
│   └── convert_corrected_jsonl_to_tei.py
├── preprocessing/
│   ├── OCR_sentence_segmentation.py
│   └── merge_txt.py
├── archive/
│   ├── convert_jsonl_to_xml_original.py
│   └── combine_merge.py
└── analysis/
    └── yearly_sentences_annotated.py

Checked_Annotations/

├── *.jsonl                     # Original Prodigy exports
├── *.cleaned.jsonl             # Automatically cleaned annotations
├── *.xml                       # XML exports generated from the original annotation .jsonl files
├── *.analysis.txt              # Annotation analysis reports
├── *.cleaned.review.csv        # Manual review and check spreadsheets
├── *.corrected.jsonl           # Manually-corrected annotations
├── *.corrected.xml             # XML exports from corrected annotations
└── *.corrected.tei.xml         # TEI-compatible XML exports
```

---

**Maintainer:** liuxduan  
**Last updated:** June 2026
