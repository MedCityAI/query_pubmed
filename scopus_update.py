import requests
import csv
import os
from datetime import datetime, timedelta

API_KEY = os.getenv("SCOPUS_API_KEY")  # store in GitHub secrets
CSV_FILE = "scopus_results.csv"

def get_scopus_results():
    # Get last 24 hours date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)

    query_url = (
        "https://api.elsevier.com/content/search/scopus"
        f"?query=PUBDATETXT({start_date.strftime('%Y%m%d')}+TO+{end_date.strftime('%Y%m%d')})"
        "&count=25"  # adjust page size
    )

    headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
    response = requests.get(query_url, headers=headers)
    response.raise_for_status()

    data = response.json()
    entries = data.get("search-results", {}).get("entry", [])
    results = []

    for e in entries:
        title = e.get("dc:title", "")
        doi = e.get("prism:doi", "")
        date = e.get("prism:coverDate", "")
        results.append([title, doi, date])

    return results

def save_to_csv(results):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Title", "DOI", "Date"])
        writer.writerows(results)

if __name__ == "__main__":
    new_results = get_scopus_results()
    if new_results:
        save_to_csv(new_results)
        print(f"Added {len(new_results)} new results.")
    else:
        print("No new results found.")
