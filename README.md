# wid-Global_index

**D5.3 – Global index representing the overall burden of diseases, including economic, social, welfare, and epidemiological aspects**

Global index of the burden of animal infectious diseases (including direct losses, compensation, denied access to international markets, etc.) and applications to 2 case studies.

---

## Overview of the workflow

```
pubmed_asf.txt
     │
     ▼
[1] pubmed2csv.py  ──►  pubmed_articles.csv
                               │
                               ▼
                   [2] clasifier.ipynb (Ollama LLM)  ──►  classified_papers.csv
                                                                  │
                                                    ┌─────────────┴──────────────┐
                                                    ▼                            ▼
                                      [3] Compare with                  [4] map.R
                                       human labels                  (world map plot)
                                    (classified_papers_metric.csv)
```

---

## Prerequisites

### 1. Miniconda (Python environment manager)

**Linux:**
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash ~/Miniconda3-latest-Linux-x86_64.sh
conda config --set auto_activate_base false
```

**macOS (Apple Silicon):**
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash ~/Miniconda3-latest-MacOSX-arm64.sh
conda config --set auto_activate_base false
```

### 2. Ollama (local LLM server)

Install Ollama from https://ollama.com and pull the required model:
```bash
ollama pull llama4        # current default model used in clasifier.ipynb
# or use a lighter alternative:
# ollama pull llama3.2
```

To monitor GPU usage while the model runs:
```bash
watch -n 0.1 nvidia-smi
```

### 3. Python environment

Create and activate a dedicated conda environment, then install dependencies:
```bash
conda create -n ollama python=3.10
conda activate ollama
pip install ollama pandas statsmodels jupyter geopandas matplotlib
```

### 4. R environment (for map visualization)

Install R (≥ 4.0) and the following packages from the R console:
```r
install.packages(c("ggplot2", "dplyr", "tidyr", "stringr"))
```

---

## Step-by-step local run

### Step 1 – Convert PubMed export to CSV

Export your PubMed search results as a **PubMed format** text file (e.g. `pubmed_asf.txt`), then run:

```bash
conda activate ollama
python pubmed2csv.py
```

**Input:** `pubmed_asf.txt` (PubMed summary text file)  
**Output:** `pubmed_articles.csv` (one row per article with PMID, Author, Date, Title, Abstract, DOI)

> To use a different input file, edit the `input_file` variable at the bottom of `pubmed2csv.py`.

---

### Step 2 – Classify papers with the LLM (Ollama)

Make sure Ollama is running in the background (it starts automatically after installation, or run `ollama serve`), then launch the notebook:

```bash
conda activate ollama
jupyter notebook clasifier.ipynb
```

Run the cells in order:
1. **Cell 0** – imports and model selection (`llama4:latest` by default; change here if needed)
2. **Cell 1** – defines the inclusion/extraction prompt
3. **Cell 2** – defines the `classify_row()` function
4. **Cell 3** – loads `pubmed_articles.csv`, runs classification, saves `classified_papers.csv`
5. **Cell 5** – prints summary statistics (totals, countries, species, methods)
6. **Cell 7** – shows a preview of the first 10 included articles

**Input:** `pubmed_articles.csv`  
**Output:** `classified_papers.csv` (original columns + classification, species, country, statistics, optimization, strategies, notes)

---

### Step 3 – Compare automatic classification with human labels

Prepare a `human_classified.csv` file with at least two columns: `PMID` and `Human` (1 = included, 0 = excluded).

Then run **Cells 8–10** of `clasifier.ipynb`:
- **Cell 8** – merges human labels into the dataframe
- **Cell 10** – computes sensitivity, specificity, accuracy with 95% CI and saves `classified_papers_metric.csv`

**Input:** `classified_papers.csv` + `human_classified.csv`  
**Output:** `classified_papers_metric.csv`

---

### Step 4 – Generate the world map

Edit `map.R` to update the `setwd()` path to your local directory, then run the script in R or RStudio:

```r
setwd("/path/to/your/wid-Global_index/")
source("map.R")
```

**Input:** `classified_papers_metric_clean.csv`  
**Output:** `world_map_disease.png` (map of included papers by country and disease)

---

## Files in this repository

| File | Description |
|------|-------------|
| `pubmed2csv.py` | Converts a PubMed text export to a structured CSV |
| `clasifier.ipynb` | Jupyter notebook: LLM classification + metrics |
| `map.R` | R script: world map of included papers by disease |
| `pubmed_asf.txt` | Example PubMed export (African Swine Fever search) |
| `classified_papers_metric.csv` | Example output with classification + metrics (comma-separated) |
| `classified_papers_metric_clean.csv` | Cleaned version of the above (semicolon-separated) |

---

## Compare automatic with human classification

Use the same PubMed CSV file to add a binary human label column (1 = include, 0 = exclude), then run the comparison cells in `clasifier.ipynb` (Cells 8–10).  
The notebook computes sensitivity, specificity, and accuracy with 95% Wilson score confidence intervals.
