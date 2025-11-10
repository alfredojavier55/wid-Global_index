# Improved Classifier Prompt

This document contains the improved version of the classification prompt based on analysis of results from June-July 2025 testing.

## Version 2.0 - Enhanced Prompt

```python
improved_prompt = """
IMPORTANT: 
Your response MUST be a single line, comma-separated, in this exact order:
  classification, species, disease, country, statistics, optimization, strategies, notes
  
Example (included):
  true, pigs, african swine fever, germany, deterministic modelling, optimization, household surveillance, meets inclusion criteria

Example (excluded):
  false, birds, avian influenza, brazil, systematic review, mentioned but not applied, unknown, excluded due to being a review

Do NOT use ";", newlines, or any other format.
Do not use any additional text or explanations outside the specified 8 columns format.

INSTRUCTIONS:
You are a systematic review expert. Evaluate every provided article title {Title} and abstract {Abstract} against the specified inclusion criteria.

1. Carefully read the article title and abstract.
   EXCLUDE:
   - Literature review articles or meta-analyses
   - Laboratory techniques without disease surveillance context (PCR, ELISA, cell culture only)
   - Studies that only mention optimization without implementing it
   - Purely descriptive studies without modelling

2. Assess whether the article meets ALL of the following inclusion criteria:

   a. Modelling: "The study must involve applied statistical modelling, mathematical simulations, 
      or predictive analytics for disease surveillance. Look for phrases like:
      - 'we developed a model'
      - 'mathematical model'
      - 'simulation study'
      - 'predictive model'
      - statistical methods applied to disease data"
      
   b. Optimization: "The study must actively apply optimization methods to improve efficiency, 
      decision-making, or predictive accuracy in disease surveillance. Evidence includes:
      - Specific optimization algorithms named (genetic algorithms, particle swarm, gradient descent)
      - Objective function defined and minimized/maximized
      - Comparison of strategies to find optimal solution
      - Phrases like 'we optimized', 'optimal strategy was determined', 'optimization problem'
      
      NOT sufficient: 'could be optimized', 'optimization is needed', 'future work will optimize'"

3. Provide your assessment using ONLY one of these two responses:
   - If ALL criteria are met: true
   - If ANY criterion is not met: false
   
   In notes field, explain in maximum 10 words the logic of the classification.

4. Extract the following information (use lowercase consistently):

   SPECIES:
   - List studied animal species using common names (e.g., 'cattle' not 'bovine')
   - If only Latin names provided and no common name exists, use Latin name
   - If multiple species, separate with spaces (e.g., 'cattle sheep goats')
   - Do NOT classify disease names as species
   - If article mentions "animals" or "livestock" without specifics, write 'general animal study'
   - If truly unclear: 'unknown'

   DISEASE:
   - Use full disease name in lowercase (e.g., 'african swine fever' not 'asf' or 'ASF')
   - If disease is implied by context but not named, extract it (e.g., if title says "ASF surveillance", use 'african swine fever')
   - Standardize common disease names: 'african swine fever', 'foot and mouth disease', 'avian influenza'
   - If multiple diseases, separate with spaces
   - If truly unclear: 'unknown'

   COUNTRY:
   - Specify country where study was conducted in lowercase
   - Look in: study site descriptions, author affiliations, methods section
   - Standardize names: 'usa' (not 'united states'), 'uk' (not 'united kingdom')
   - If multiple countries, separate with spaces
   - If study is global or multi-continental, write 'worldwide' or 'global'
   - If region mentioned without specific country, use region: 'sub-saharan africa', 'southeast asia'
   - If truly unclear: 'unknown'

   STATISTICS:
   - List statistical methods applied (e.g., 'regression analysis', 'bayesian inference', 
     'mechanistic models', 'compartment models', 'machine learning')
   - Look for phrases: 'we used', 'we applied', 'statistical analysis included', 'methods:'
   - Use standard terms: 'deterministic modelling', 'stochastic modelling', 'regression analysis'
   - If multiple methods, separate with spaces
   - If truly unclear: 'unknown'

   OPTIMIZATION:
   - If optimization methods actively applied: name the method (e.g., 'optimal control', 
     'genetic algorithm', 'multi-objective optimization')
   - If optimization mentioned but NOT implemented: 'mentioned but not applied'
   - Look for: algorithm names, objective functions, optimization results shown
   - If truly unclear: 'unknown'

   STRATEGIES:
   - Extract recommended surveillance strategies (e.g., 'risk-based monitoring', 
     'early-warning systems', 'targeted surveillance')
   - If article recommends control strategies, list them (e.g., 'vaccination', 'culling', 'quarantine')
   - If multiple strategies, separate with spaces
   - If truly unclear: 'unknown'

5. Follow these strict rules:
   - Base assessment solely on information in title and abstract
   - Use lowercase consistently for ALL extracted fields
   - Use spaces (not commas) to separate multiple values within a field
   - If information is unclear or not stated, write 'unknown'
   - For optimization: distinguish "mentioned" from "applied" carefully
   - ONLY use one line, DO NOT deviate from the format
   - Total output must be exactly 8 comma-separated values

Your task is to provide a clear, binary assessment and extract information as described above, 
in single-line format with exactly 8 fields.
"""
```

## Key Improvements from Original Prompt

### 1. Better Guidance for Reducing "Unknown" Entries

**Original Issue:** 20-40% unknown rates for species, country, disease fields

**Improvements:**
- Added explicit fallback options ("general animal study" instead of unknown for unspecified animals)
- Instructions to look in specific places (author affiliations, methods)
- Guidance to use region names when specific country unavailable
- Emphasis on extracting implied information from context

### 2. Enhanced Consistency

**Original Issue:** Same entity written multiple ways (ASF vs african swine fever)

**Improvements:**
- Explicit standardization rules (usa not united states)
- Examples of standardized disease names
- Consistent lowercase requirement emphasized
- Common name preference for species

### 3. Clearer Optimization Detection

**Original Issue:** Confusion between "optimization mentioned" vs "optimization applied"

**Improvements:**
- Specific phrases to look for that indicate actual optimization
- Counter-examples of what doesn't count (future work, could be optimized)
- Evidence required: algorithm names, objective functions, optimization results

### 4. Better Structured Guidance

**Improvements:**
- Each field has its own section with clear instructions
- Specific phrases to look for in the abstract
- Multiple examples for each field type
- Consistent format throughout

## Usage Example

```python
import pandas as pd
import ollama

# Use the improved prompt
model = "llama4:latest"

def classify_row_improved(row):
    prompt_text = f"{improved_prompt}\n\nTitle: {row['Title']}\nAbstract: {row['Abstract']}"
    response = ollama.generate(
        model=model,
        prompt=prompt_text
    )
    
    parts = [p.strip() for p in response['response'].strip().lower().split(',')]
    
    # Ensure we always have 8 parts
    while len(parts) < 8:
        parts.append('unknown')
    
    classification, species, disease, country, statistics, optimization, strategies, notes = parts[:8]
    
    return pd.Series({
        'classification': 'included' if classification == 'true' else 'not included',
        'species': species,
        'disease': disease,
        'country': country,
        'statistics': statistics,
        'optimization': optimization,
        'strategies': strategies,
        'notes': notes
    })

# Apply to dataframe
df = pd.read_csv('pubmed_articles.csv')
df[['classification', 'species', 'disease', 'country', 'statistics', 
    'optimization', 'strategies', 'notes']] = df.apply(classify_row_improved, axis=1)
df.to_csv('classified_papers_v2.csv', index=False)
```

## Expected Improvements

Based on analysis of previous results, this improved prompt should:

1. **Reduce "unknown" rates by 30-50%**
   - Species: from ~40% to ~20%
   - Country: from ~50% to ~25%
   - Disease: from ~30% to ~15%

2. **Improve consistency**
   - Eliminate variant spellings (ASF vs african swine fever)
   - Standardize country names
   - Consistent capitalization

3. **Better optimization detection**
   - Reduce false positives from "optimization mentioned" cases
   - More accurate categorization

4. **Maintain or improve performance metrics**
   - Target: 90%+ sensitivity
   - Target: 95%+ specificity
   - Target: 92%+ accuracy

## Testing Recommendations

1. Test on subset of 100 articles first
2. Compare results with original prompt
3. Measure unknown rates for each field
4. Validate against human classifications
5. Iterate based on results

## Next Version Ideas (v3.0)

Future improvements to consider:

1. **Two-stage extraction**: First classify, then detailed extraction for included articles
2. **Confidence scoring**: Add confidence field (1-5) for each classification
3. **Field-specific prompts**: Separate prompts optimized for each extraction field
4. **Chain-of-thought**: Ask model to explain reasoning before providing answer
5. **Few-shot examples**: Include 3-5 real examples from the dataset
