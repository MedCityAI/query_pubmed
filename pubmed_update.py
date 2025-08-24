import requests
import csv
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

CSV_FILE = "pubmed_results.csv"

def get_pubmed_results():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=3)
    start_str = start_date.strftime("%Y/%m/%d")
    end_str = end_date.strftime("%Y/%m/%d")
    date_query = f'("{start_str}"[PDAT] : "{end_str}"[PDAT])'

    aff_queries = [
        '"Rochester, MN"',
        '"Rochester, Minnesota"',
        '"Rochester, Min"',
        '"Rochester, Minn"',
    ]
    aff_query = "(" + " OR ".join(aff_queries) + ")"
    full_query = f"{date_query} AND {aff_query}"

    params = {
        "db": "pubmed",
        "term": full_query,
        "retmax": "100",
        "retmode": "json"
    }
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    r = requests.get(esearch_url, params=params)
    r.raise_for_status()
    pmids = r.json().get("esearchresult", {}).get("idlist", [])

    if not pmids:
        return []

    id_str = ",".join(pmids)
    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": id_str,
        "retmode": "json"
    }
    r2 = requests.get(esummary_url, params=params)
    r2.raise_for_status()
    docs = r2.json().get("result", {})

    results = []
    for pmid in pmids:
        doc = docs.get(pmid, {})
        title = doc.get("title", "")
        authors = ", ".join(a["name"] for a in doc.get("authors", []) if "name" in a)
        citation = ""
        first_author = doc.get("sortfirstauthor", "")
        journal_abbrev = doc.get("source", "")
        todaydate = datetime.today()
        formatted_date = todaydate.strftime("%Y/%m/%d")
        formatted_year = todaydate.strftime("%Y")
        year = formatted_year
        pubdate = formatted_date
        journal = doc.get("fulljournalname", "")
        affiliation = ""
        doi = ""
        results.append([pmid, title, authors, citation, first_author, journal_abbrev, year, pubdate, journal, affiliation, doi])

    return results

def save_to_csv(results):
    existing = set()
    if os.path.isfile(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if row and row[0] != "PMID":
                    existing.add(row[0])
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existing:
            writer.writerow(["pmid", "title", "authors", "citation", "first_author", "journal_abbrev", "year", "pubdate", "journal", "affiliation", "doi"])
        for row in results:
            if row[0] not in existing:
                writer.writerow(row)

if __name__ == "__main__":
    new = get_pubmed_results()
    if new:
        save_to_csv(new)
        print(f"Added {len(new)} new results.")
    else:
        print("No new results found.")
