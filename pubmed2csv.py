import csv

def parse_pubmed_file(input_file):
    """Reads and extracts article details from a PubMed text file."""
    articles = []
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    raw_articles = content.strip().split('\n\n')

    for raw in raw_articles:
        pmid = ""
        first_author = ""
        pub_date = ""
        doi = ""
        title_lines = []
        abstract_lines = []
        in_title = in_abstract = False

        for line in raw.split('\n'):
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
            elif in_abstract and line.startswith("      "):
                abstract_lines.append(line.strip())
            elif line.startswith("AID -") and "[doi]" in line:
                doi = line.replace("AID -", "").replace("[doi]", "").strip()
                in_title = in_abstract = False
            else:
                in_title = in_abstract = False

        title = " ".join(title_lines)
        abstract = " ".join(abstract_lines)

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
        writer = csv.DictWriter(file, fieldnames=["PMID", "First Author", "Publication Date", "Title", "Abstract", "DOI"])
        writer.writeheader()
        writer.writerows(articles)

# Example usage
input_file = "pubmed_asf.txt"  # Replace with your actual file path
output_file = "pubmed_articles.csv"

articles = parse_pubmed_file(input_file)
write_to_csv(articles, output_file)

print(f"Processed {len(articles)} articles. Data saved to {output_file}.")