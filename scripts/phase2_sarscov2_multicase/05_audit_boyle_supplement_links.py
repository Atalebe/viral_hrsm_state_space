from pathlib import Path
import re
import urllib.request
import urllib.error
import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]

ARTICLE_URLS = [
    "https://www.mdpi.com/1999-4915/17/10/1313",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC12567731/",
]

OUT_DIR = ROOT / "metadata" / "phase2_sarscov2_multicase"
OUT_LINKS = OUT_DIR / "boyle_supplement_link_audit.csv"
OUT_HTML_SUMMARY = OUT_DIR / "boyle_article_link_summary.csv"

def fetch(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            return {
                "ok": True,
                "status": getattr(response, "status", ""),
                "html": response.read().decode("utf-8", errors="replace"),
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "html": "",
            "error": f"HTTPError: {exc.code} {exc.reason}",
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": "",
            "html": "",
            "error": f"{type(exc).__name__}: {exc}",
        }

def classify_link(text, href):
    hay = f"{text} {href}".lower()
    tags = []

    if "supplement" in hay or "supporting" in hay:
        tags.append("supplement_candidate")
    if "table" in hay:
        tags.append("table_candidate")
    if "s1" in hay or "s 1" in hay or "supplementary table s1" in hay:
        tags.append("supplementary_table_s1_candidate")
    if href.lower().endswith((".xlsx", ".xls", ".csv", ".tsv", ".txt", ".zip", ".docx", ".pdf")):
        tags.append("downloadable_file_candidate")
    if "download" in hay:
        tags.append("download_candidate")
    if "prjna1295507" in hay or "sra" in hay or "samn" in hay or "srr" in hay:
        tags.append("accession_candidate")

    if not tags:
        tags.append("unclassified")

    return ";".join(tags)

def absolute_url(base_url, href):
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return urllib.request.urljoin(base_url, href)

def parse_links(url, html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    all_text = soup.get_text(" ", strip=True)
    accession_hits = sorted(set(re.findall(r"(PRJNA\d+|SRR\d+|SAMN\d+)", all_text)))

    summary = {
        "url": url,
        "fetch_ok": True,
        "status": 200,
        "error": "",
        "title": title,
        "html_chars": len(html),
        "text_chars": len(all_text),
        "accession_hits": "|".join(accession_hits[:50]),
        "n_accession_hits": len(accession_hits),
        "mentions_supplement": "supplement" in all_text.lower(),
        "mentions_table_s1": bool(re.search(r"table\s+s1|supplementary\s+table\s+s1", all_text, re.I)),
    }

    rows = []

    for a in soup.find_all("a"):
        href = a.get("href") or ""
        text = a.get_text(" ", strip=True)

        if not href and not text:
            continue

        href_abs = absolute_url(url, href)
        tags = classify_link(text, href_abs)

        if tags != "unclassified":
            rows.append({
                "source_url": url,
                "anchor_text": text,
                "href": href_abs,
                "tags": tags,
            })

    return summary, rows

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    link_rows = []
    summary_rows = []

    for url in ARTICLE_URLS:
        print({"status": "fetching", "url": url})
        result = fetch(url)

        if not result["ok"]:
            summary_rows.append({
                "url": url,
                "fetch_ok": False,
                "status": result["status"],
                "error": result["error"],
                "title": "",
                "html_chars": 0,
                "text_chars": 0,
                "accession_hits": "",
                "n_accession_hits": 0,
                "mentions_supplement": False,
                "mentions_table_s1": False,
            })
            print({"status": "fetch_failed_continuing", "url": url, "error": result["error"]})
            continue

        summary, links = parse_links(url, result["html"])
        summary_rows.append(summary)
        link_rows.extend(links)

    links = pd.DataFrame(link_rows)
    if links.empty:
        links = pd.DataFrame(columns=["source_url", "anchor_text", "href", "tags"])
    else:
        links = links.drop_duplicates()

    summary = pd.DataFrame(summary_rows)

    links.to_csv(OUT_LINKS, index=False)
    summary.to_csv(OUT_HTML_SUMMARY, index=False)

    print({
        "status": "wrote",
        "links": str(OUT_LINKS),
        "summary": str(OUT_HTML_SUMMARY),
        "n_links": len(links),
        "n_sources": len(summary),
        "n_fetch_ok": int(summary["fetch_ok"].sum()) if "fetch_ok" in summary else 0,
    })

    print("\nSOURCE SUMMARY")
    print(summary.to_string(index=False))

    print("\nLINK CANDIDATES")
    if len(links):
        print(links.to_string(index=False))
    else:
        print("No supplement/accession/table links found from fetchable pages.")

if __name__ == "__main__":
    main()
