import csv
import re

def parse_pubmed_file(input_file):
    """Reads and extracts article details from a PubMed text file."""
    articles = []
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split articles by PMID- (keep the PMID- line with each block)
    raw_articles = re.split(r'(?=^PMID-)', content, flags=re.MULTILINE)

    for raw in raw_articles:
        if not raw.strip():
            continue
        pmid = ""
        first_author = ""
        pub_date = ""
        doi = ""
        title_lines = []
        abstract_lines = []
        in_title = in_abstract = False

        for line in raw.replace('\r\n', '\n').split('\n'):
            if line.startswith("PMID-"):
                pmid = line.replace("PMID-", "").strip()
                in_title = in_abstract = False
            elif (line.startswith("AU -") or line.startswith("AU  -")) and not first_author:
                first_author = line.split("-", 1)[1].strip()
                in_title = in_abstract = False
            elif (line.startswith("DP -") or line.startswith("DP  -")):
                pub_date = line.split("-", 1)[1].strip()
                in_title = in_abstract = False
            elif line.startswith("TI  -"):
                title_lines.append(line.replace("TI  -", "").strip())
                in_title = True
                in_abstract = False
            elif in_title and line.startswith("      "):
                title_lines.append(line.strip())
            elif line.startswith("AB  -"):
                abstract_lines.append(line.replace("AB  -", "").strip())
                in_abstract = True
                in_title = False
            elif in_abstract and not re.match(r'^[A-Z]{2,4}\s*-', line):
                abstract_lines.append(line.strip())
            elif re.match(r'^\s*(AID|LID)\s*-\s*', line):
                candidate = re.sub(r'^\s*(AID|LID)\s*-\s*', '', line)
                candidate = candidate.replace("[doi]", "").strip()
                if not doi and "/" in candidate and not candidate.isdigit():
                    doi = candidate
                in_title = in_abstract = False
            else:
                in_title = in_abstract = False

        title = " ".join(title_lines)
        abstract = " ".join(abstract_lines)
        
        # Replace semicolons with commas or periods
        abstract = abstract.replace(";", ".")  # Change to "." to avoid spliting on semicolons when oppened in Excel
        
        # Remove tabs and newlines from all fields
        title = title.replace('\t', ' ').replace('\n', ' ')
        abstract = abstract.replace('\t', ' ').replace('\n', ' ')
        first_author = first_author.replace('\t', ' ').replace('\n', ' ')
        pub_date = pub_date.replace('\t', ' ').replace('\n', ' ')
        doi = doi.replace('\t', ' ').replace('\n', ' ')

        if pmid:
            articles.append({
                "PMID": pmid,
                "First Author": first_author,
                "Publication Date": pub_date,
                "Title": title,
                "Abstract": abstract,
                "DOI": doi if doi else "N/A"
            })

    return articles

def write_to_csv(articles, output_file):
    """Writes extracted PubMed data into a CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["PMID", "First Author", "Publication Date", "Title", "Abstract", "DOI"], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(articles)

# Example usage
input_file = "pubmed_asf.txt"  # Replace with your actual file path
output_file = "pubmed_articles_asf.csv"

articles = parse_pubmed_file(input_file)
write_to_csv(articles, output_file)

print(f"Processed {len(articles)} articles. Data saved to {output_file}.")