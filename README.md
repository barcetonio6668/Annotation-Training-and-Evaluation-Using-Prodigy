# 🏔️ Named Entity Recognition with Prodigy — Alpine Journal Project

This project uses [Prodigy](https://prodi.gy/) for annotating and training a custom Named Entity Recognition (NER) model on texts from the **British Alpine Journal (mainly 2020–2022)**. The goal is to extract entities such as mountain names, valleys, cities, people, countries, and dates.

🚀 Workflow Summary

1️⃣ Activate the Virtual Environment

```bash
cd /path/to/project-folder
source venv/bin/activate

2️⃣ Start Annotation Interface

prodigy ner.correct golden_standard_dataset en_core_web_sm "path/to/your/annotation/data.txt" --label PERSON,MOUNTAIN,VALLEY,CITY,GPE,DATE

# This will launch Prodigy at http://localhost:8080.
# en_core_web_sm is a base model from SpaCy for English
# When you're done annotating, press Ctrl+C in the terminal to safely exit and save your work.

3️⃣ Export the Annotations (JSONL format)
## If you have not configured anything specifically, 
## Prodigy defaults to using an SQLite database located 
## in your working directory, at the following path:

.prodigy/prodigy.db

# Saving Command:

prodigy db-out your_dataset_name > annotations.jsonl

4️⃣ Train a Custom NER Model with Prodigy

prodigy train model_name_of_your_choice --ner golden_standard_dataset --base-model path_to_your_baseline_model

5️⃣ Use the Trained Model (Inference Example)

import spacy

nlp = spacy.load("ner-model/model-best")
doc = nlp("John Smith climbed Mount Everest in 2021.") # Your example sentence
for ent in doc.ents:
    print(ent.text, ent.label_)

## Maintainer: liuxduan
## Last updated: June 2025
