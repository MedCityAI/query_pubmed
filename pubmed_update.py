import requests
import csv
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

CSV_FILE = "pubmed_results.csv"

def get_pubmed_results():
    # Time range: last 24h
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)

    # Format for PubMed (YYYY/MM/DD)
    start_str = start_date.strftime("%Y/%m/%d")
    end_str = end_date.strftime("%Y/%m/%d")

    # ESearch: find PMIDs
    esearch_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&term=({start_str}[PDAT] : {end_str}[PDAT])"
        "&retmax=100&retmode=json"
    )
    esearch_resp = requests.get(esearch_url)
    esearch_resp.raise_for_status()
    pmids = esearch_resp.json().get("esearchresult", {}).get("idlist", [])

    if not pmids:
        return []

    # ESummary: fetch metadata for these PMIDs
    id_str = ",".join(pmids)
    esummary_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=pubmed&id={id_str}&retmode=json"
    )
    esummary_resp = requests.get(esummary_url)
    esummary_resp.raise_for_status()
    docsums = esummary_resp.json().get("result", {})

    results = []
    for pmid in pmids:
        doc = docsums.get(pmid, {})
        title = doc.get("title", "")
        journal = doc.get("fulljournalname", "")
        pubdate = doc.get("pubdate", "")
        authors = ", ".join([a["name"] for a in doc.get("authors", []) if "name" in a])
        results.append([pmid, title, journal, pubdate, authors])

    return results


def save_to_csv(results):
    file_exists = os.path.isfile(CSV_FILE)
    existing_pmids = set()

    # Prevent duplicates
    if file_exists:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row:
                    existing_pmids.add(row[0])

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["PMID", "Title", "Journal", "PubDate", "Authors"])
        for row in results:
            if row[0] not in existing_pmids:
                writer.writerow(row)


if __name__ == "__main__":
    new_results = get_pubmed_results()
    if new_results:
        save_to_csv(new_results)
        print(f"Added {len(new_results)} new results.")
    else:
        print("No new results found.")
