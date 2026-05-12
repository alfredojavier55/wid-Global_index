# wid-Optimization-literature review

D5.3 – Optimization of Surveillance 

## 📚 Literature Review Automation

This repository contains an automated literature classification system using Large Language Models (LLMs) to screen scientific articles for systematic reviews in disease surveillance.

### 🎯 Key Features

- **Automated Classification**: Uses LLMs (Llama, Mistral) via Ollama to classify articles based on inclusion criteria
- **Structured Data Extraction**: Extracts 7 fields: species, disease, country, statistics, optimization, strategies, notes
- **Performance Validated**: Achieves up to 97.6% specificity and 90.1% accuracy
- **Multiple Models Tested**: Llama 3.1, 3.2, 4, and Mistral variants
- **Quality Assurance**: Automated quality checking and consistency validation

### 📊 Performance Summary

Based on testing from June-July 2025 (see [CLASSIFIER_IMPLEMENTATION_REPORT.md](CLASSIFIER_IMPLEMENTATION_REPORT.md)):

| Model | Sensitivity | Specificity | Accuracy | Best For |
|-------|-------------|-------------|----------|----------|
| Llama 4 (28.06) | 100.0% | 94.4% | 94.4% | High-recall screening |
| Llama 3.1 (02.07) | 76.2% | 97.8% | 97.6% | High-precision selection |
| Llama 4 (01.07) | 89.4% | 90.2% | 90.1% | Balanced screening |

## 🚀 Quick Start

### 1. Installation

**Option A: Using Conda (Recommended)**

```bash
# Create environment
conda create -n ollama python=3.10
conda activate ollama

# Install dependencies
pip install -r requirements.txt

# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download
```

**Option B: Using pip**
(on personal computers)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Ollama
On KITA server there is no need to install Ollama, pull.
```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull llama4:latest
# Or: ollama pull llama3.1:8b

# Verify installation
ollama list
```

### 3. Prepare Your Data

```bash
# Convert PubMed export to CSV
python pubmed2csv.py pubmed_asf.txt

# This creates: pubmed_articles.csv
```

### 4. Run Classification

**Option A: Using Jupyter Notebook**

```bash
jupyter notebook clasifier.ipynb
```

**Option B: Using Python Script** (if you create one)

```python
import pandas as pd
import ollama

# Load your improved prompt
from IMPROVED_PROMPT import improved_prompt

model = "llama4:latest"

def classify_row(row):
    prompt_text = f"{improved_prompt}\n\nTitle: {row['Title']}\nAbstract: {row['Abstract']}"
    response = ollama.generate(model=model, prompt=prompt_text)
    # ... rest of classification logic
    
df = pd.read_csv('pubmed_articles.csv')
# Apply classification...
```

### 5. Analyze Results

```bash
# Run automated quality analysis
python automated_analysis.py classified_papers.csv human_classified.csv

# This generates:
# - analysis_report.md (comprehensive report)
# - classified_papers_with_quality_checks.csv (enhanced dataset)
```

## 📁 Repository Structure

```
wid-Global_index/
├── clasifier.ipynb                           # Main classification notebook
├── pubmed2csv.py                             # PubMed text to CSV converter
├── automated_analysis.py                     # Quality analysis tool (NEW)
├── CLASSIFIER_IMPLEMENTATION_REPORT.md       # Detailed analysis report (NEW)
├── IMPROVED_PROMPT.md                        # Enhanced prompt v2.0 (NEW)
├── requirements.txt                          # Python dependencies (NEW)
├── README.md                                 # This file (UPDATED)
│
├── results/                                  # Classification results archive
│   ├── 28.06.25.txt                         # Llama 4 - perfect sensitivity
│   ├── 30.06.25.txt                         # Llama 3.2 comparison
│   ├── 01.07.25.txt                         # Llama 4 balanced
│   ├── 02.07.25 llama3.1.txt                # Llama 3.1 - highest specificity
│   ├── 03.07.25.txt                         # Extended fields test
│   ├── 03.07.25 llama3.1 161.txt            # Most conservative
│   ├── 08.07.25.txt                         # Mistral comparison
│   └── 15.07.25 llama3.1 148.txt            # Final optimization
│
├── classified_papers_metric.csv              # Latest classification results
└── classified_papers_metric_clean.csv        # Cleaned version
```

## 🔍 Workflow

### Step 1: Data Preparation

```bash
# Get PubMed articles (example search)
# Go to PubMed, search for your topic, export as "PubMed" format

# Convert to CSV
python pubmed2csv.py pubmed_asf.txt
```

**Input format** (PubMed text export):
```
PMID- 12345678
TI  - Article Title Here
AB  - Abstract text here...
AU  - Author1 A
FAU - Author1, A
...
```

**Output format** (CSV):
```csv
PMID,First Author,Publication Date,Title,Abstract,DOI
12345678,Author1 A,2024,Article Title Here,Abstract text...,10.1234/...
```

### Step 2: Classification

Open `clasifier.ipynb` and run cells to:

1. Load the CSV
2. Apply classification function to each row
3. Extract structured information
4. Save results

**Classification extracts:**
- ✅ **Classification**: included/not included
- 🐾 **Species**: Animal species studied
- 🦠 **Disease**: Disease being studied  
- 🌍 **Country**: Study location
- 📊 **Statistics**: Statistical methods used
- ⚡ **Optimization**: Optimization methods applied
- 🎯 **Strategies**: Surveillance strategies recommended
- 📝 **Notes**: Brief reasoning for classification

### Step 3: Quality Analysis

```bash
python automated_analysis.py classified_papers_metric.csv human_classified.csv
```

**Quality checks performed:**
- Consistency validation (e.g., species in correct field)
- Unknown rate calculation for each field
- Performance metrics vs human classification
- Issue detection and flagging

**Outputs:**
- `analysis_report.md`: Comprehensive quality report
- `*_with_quality_checks.csv`: Enhanced CSV with issue flags

### Step 4: Validation

Compare against human classification:

```python
# In your notebook or script
import pandas as pd

# Load human classifications
human_df = pd.read_csv('human_classified.csv', delimiter=';')

# Add human column to classified data
df['human'] = df['PMID'].isin(
    human_df.loc[human_df['Human'] == 1, 'PMID']
).astype(int)

# Calculate metrics (sensitivity, specificity, accuracy)
# See clasifier.ipynb for full implementation
```

## 📈 Improvements in This Version

### 1. Comprehensive Documentation

✅ **NEW**: [CLASSIFIER_IMPLEMENTATION_REPORT.md](CLASSIFIER_IMPLEMENTATION_REPORT.md)
- Chronological analysis of all testing phases (June 28 - July 15, 2025)
- Detailed performance comparison of all models
- Evolution of prompt and extraction fields
- Recommendations for model selection based on use case

### 2. Automated Quality Analysis

✅ **NEW**: [automated_analysis.py](automated_analysis.py)
- Automatic consistency checking
- Quality metrics calculation  
- Unknown rate tracking
- Performance validation
- Markdown report generation

**Features:**
```python
# Check for issues like:
- Country names in species field
- Included articles without optimization
- Disease identified but species unknown
- Calculate unknown rates for all fields
- Generate comprehensive reports
```

### 3. Improved Prompt

✅ **NEW**: [IMPROVED_PROMPT.md](IMPROVED_PROMPT.md)

**Key improvements:**
- Better guidance to reduce "unknown" entries (30-50% reduction expected)
- Explicit standardization rules (consistent naming)
- Clearer optimization detection (mentioned vs applied)
- Field-specific extraction instructions
- More examples for each category

**Expected performance:**
- Unknown rate: Species ~20% (was ~40%)
- Unknown rate: Country ~25% (was ~50%)
- Unknown rate: Disease ~15% (was ~30%)
- Maintained: 90%+ sensitivity, 95%+ specificity

### 4. Suggested Enhancements

**A. Two-Stage Classification**
```python
# Stage 1: High-recall with Llama 4 (catch all relevant)
# Stage 2: High-precision with Llama 3.1 (filter false positives)
```

**B. Ensemble Classification**
```python
# Run with 3 models, require 2/3 agreement
# Reduces both false positives and false negatives
```

**C. Confidence Scoring**
```python
# Add confidence field (1-5) to identify uncertain cases
# Flag articles needing human review
```

**D. Active Learning**
```python
# Learn from human corrections
# Iteratively improve prompt based on errors
```

## 🎓 Usage Examples

### Example 1: High-Recall Screening

```python
# Use Llama 4 with original prompt from 28.06.25
model = "llama4:latest"
# Achieves 100% sensitivity - catches all relevant articles
# Some false positives acceptable at this stage
```

### Example 2: High-Precision Final Selection

```python
# Use Llama 3.1 8B with strict criteria
model = "llama3.1:8b"
# Achieves 97.8% specificity - minimizes false positives
# May miss some edge cases (76.2% sensitivity)
```

### Example 3: Balanced Approach

```python
# Use Llama 4 with refined prompt from 01.07.25
model = "llama4:latest"
# Balanced: ~90% sensitivity, ~90% specificity
# Good for single-pass classification
```

### Example 4: Hybrid Two-Stage

```python
# Stage 1: Llama 4 (high recall)
df_stage1 = classify_all(df, "llama4:latest", sensitive_prompt)
included_stage1 = df_stage1[df_stage1['classification'] == 'included']

# Stage 2: Llama 3.1 (high precision) 
df_final = classify_all(included_stage1, "llama3.1:8b", specific_prompt)
final_included = df_final[df_final['classification'] == 'included']
```

## 📊 Results Archive

The `results/` folder contains outputs from all testing phases:

- **28.06.25.txt**: Llama 4 baseline (100% sensitivity)
- **30.06.25.txt**: Llama 3.2 comparison (faster but less accurate)
- **01.07.25.txt**: Llama 4 refined (balanced performance)
- **02.07.25 llama3.1.txt**: Llama 3.1 (highest specificity)
- **03.07.25.txt**: Extended fields (7 → 10 fields)
- **08.07.25.txt**: Mistral alternative
- **15.07.25 llama3.1 148.txt**: Final optimized version

Each file contains:
- Runtime information
- Performance metrics (sensitivity, specificity, accuracy)
- Confusion matrix
- Distribution of extracted fields
- Top categories for included articles

## 🔧 Troubleshooting

### Issue: High "unknown" rates

**Solution**: Use the improved prompt in `IMPROVED_PROMPT.md`

### Issue: Inconsistent naming

**Solution**: The improved prompt includes standardization rules

### Issue: False positives (optimization "mentioned" classified as included)

**Solution**: Use Llama 3.1 model or improved prompt with clearer criteria

### Issue: Model too slow

**Solution**: Use Llama 3.2 for faster processing (trade-off: lower accuracy)

### Issue: Need higher precision

**Solution**: Use Llama 3.1 (97.8% specificity) or two-stage approach

## 📚 Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [PubMed Search Tips](https://pubmed.ncbi.nlm.nih.gov/help/)
- Systematic Review Guidelines: PRISMA

## 🤝 Contributing

To improve the classifier:

1. Test new prompts and document results
2. Add new models and compare performance
3. Suggest improvements to extraction logic
4. Report issues with specific examples

## 📝 Citation

If you use this classifier in your research, please cite:

```
[Add citation information here once published]
```

## 📞 Support

For questions or issues:
- Check the [CLASSIFIER_IMPLEMENTATION_REPORT.md](CLASSIFIER_IMPLEMENTATION_REPORT.md) for detailed analysis
- Review the [IMPROVED_PROMPT.md](IMPROVED_PROMPT.md) for prompt guidance
- Open an issue in the repository

## ⚖️ License

[Add license information]

---

**Last Updated**: November 2025  
**Version**: 2.0  
**Status**: Production-ready with documented improvements 
