from pathlib import Path
import re
import urllib.request
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]

ARTICLE_URLS = [
    "https://www.nature.com/articles/s41467-021-26602-3",
    "https://pmc.ncbi.nlm.nih.gov/articles/PMC8583298/",
]

OUT_DIR = ROOT / "metadata" / "phase2_sarscov2_multicase"
OUT_ARTICLE_SUMMARY = OUT_DIR / "weigang_article_accession_summary.csv"
OUT_LINKS = OUT_DIR / "weigang_article_links.csv"
OUT_ACCESSIONS = OUT_DIR / "weigang_accession_candidates.csv"
OUT_ENA_AUDIT = OUT_DIR / "weigang_ena_accession_audit.csv"

FIELDS = [
    "study_accession",
    "secondary_study_accession",
    "sample_accession",
    "experiment_accession",
    "run_accession",
    "tax_id",
    "scientific_name",
    "instrument_platform",
    "instrument_model",
    "library_layout",
    "library_strategy",
    "read_count",
    "base_count",
    "fastq_ftp",
    "submitted_ftp",
    "bam_ftp",
    "sample_title",
    "experiment_title",
]

ACCESSION_RE = re.compile(
    r"\b(PRJNA\d+|PRJEB\d+|SRP\d+|ERP\d+|SRR\d+|ERR\d+|SAMN\d+|ERS\d+|EPI_ISL_\d+|GSE\d+)\b"
)

def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")

def try_fetch(url):
    try:
        html = fetch(url)
        return True, 200, "", html
    except Exception as exc:
        return False, "", f"{type(exc).__name__}: {exc}", ""

def fetch_ena(accession):
    params = {
        "accession": accession,
        "result": "read_run",
        "fields": ",".join(FIELDS),
        "format": "tsv",
        "download": "true",
        "limit": "0",
    }
    url = "https://www.ebi.ac.uk/ena/portal/api/filereport?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")

def classify_link(text, href):
    hay = f"{text} {href}".lower()
    tags = []
    if "supplement" in hay or "supporting" in hay or "additional file" in hay:
        tags.append("supplement_candidate")
    if "data" in hay or "availability" in hay:
        tags.append("data_candidate")
    if href.lower().endswith((".xlsx", ".xls", ".csv", ".tsv", ".txt", ".zip", ".pdf", ".docx")):
        tags.append("downloadable_candidate")
    if any(k in hay for k in ["sra", "ena", "ncbi", "prjna", "prjeb", "srr", "err", "samn", "gisaid", "epi_isl"]):
        tags.append("accession_candidate")
    return ";".join(tags) if tags else "unclassified"

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    link_rows = []
    accession_rows = []

    for url in ARTICLE_URLS:
        print({"status": "fetching_article", "url": url})
        ok, status, error, html = try_fetch(url)

        if not ok:
            summary_rows.append({
                "article_url": url,
                "fetch_ok": False,
                "status": status,
                "error": error,
                "title": "",
                "html_chars": 0,
                "text_chars": 0,
                "n_accession_candidates": 0,
                "accession_candidates": "",
                "mentions_data_availability": False,
                "mentions_supplement": False,
            })
            continue

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        accessions = sorted(set(ACCESSION_RE.findall(text)))

        summary_rows.append({
            "article_url": url,
            "fetch_ok": True,
            "status": status,
            "error": "",
            "title": soup.title.string.strip() if soup.title and soup.title.string else "",
            "html_chars": len(html),
            "text_chars": len(text),
            "n_accession_candidates": len(accessions),
            "accession_candidates": "|".join(accessions[:150]),
            "mentions_data_availability": "data availability" in text.lower(),
            "mentions_supplement": "supplement" in text.lower() or "additional file" in text.lower(),
        })

        for acc in accessions:
            accession_rows.append({
                "article_url": url,
                "accession": acc,
                "accession_prefix": re.match(r"[A-Z_]+", acc).group(0),
            })

        for a in soup.find_all("a"):
            href = a.get("href") or ""
            text_a = a.get_text(" ", strip=True)
            if not href and not text_a:
                continue

            href_abs = urllib.request.urljoin(url, href)
            tags = classify_link(text_a, href_abs)
            if tags != "unclassified":
                link_rows.append({
                    "article_url": url,
                    "anchor_text": text_a,
                    "href": href_abs,
                    "tags": tags,
                })

    summary = pd.DataFrame(summary_rows)
    links = pd.DataFrame(link_rows).drop_duplicates() if link_rows else pd.DataFrame(columns=["article_url", "anchor_text", "href", "tags"])
    accession_df = pd.DataFrame(accession_rows).drop_duplicates() if accession_rows else pd.DataFrame(columns=["article_url", "accession", "accession_prefix"])

    summary.to_csv(OUT_ARTICLE_SUMMARY, index=False)
    links.to_csv(OUT_LINKS, index=False)
    accession_df.to_csv(OUT_ACCESSIONS, index=False)

    ena_rows = []

    project_accessions = accession_df[
        accession_df["accession"].astype(str).str.match(r"^(PRJNA|PRJEB|SRP|ERP)")
    ]["accession"].drop_duplicates().tolist()

    for acc in project_accessions:
        print({"status": "fetching_ena", "accession": acc})
        raw_path = OUT_DIR / f"weigang_{acc.lower()}_ena_read_run.tsv"
        try:
            tsv = fetch_ena(acc)
            raw_path.write_text(tsv, encoding="utf-8")
            df = pd.read_csv(raw_path, sep="\t") if tsv.strip() else pd.DataFrame()

            ena_rows.append({
                "accession": acc,
                "raw_table": str(raw_path.relative_to(ROOT)),
                "n_rows": len(df),
                "n_unique_samples": df["sample_accession"].nunique() if "sample_accession" in df else 0,
                "n_unique_runs": df["run_accession"].nunique() if "run_accession" in df else 0,
                "has_fastq_ftp": bool(df.get("fastq_ftp", pd.Series(dtype=str)).fillna("").astype(str).str.len().gt(0).any()),
                "has_submitted_ftp": bool(df.get("submitted_ftp", pd.Series(dtype=str)).fillna("").astype(str).str.len().gt(0).any()),
                "status": "queried",
                "error": "",
            })
        except Exception as exc:
            ena_rows.append({
                "accession": acc,
                "raw_table": "",
                "n_rows": 0,
                "n_unique_samples": 0,
                "n_unique_runs": 0,
                "has_fastq_ftp": False,
                "has_submitted_ftp": False,
                "status": "query_failed",
                "error": f"{type(exc).__name__}: {exc}",
            })

    ena_audit = pd.DataFrame(ena_rows)
    ena_audit.to_csv(OUT_ENA_AUDIT, index=False)

    print({
        "status": "wrote",
        "article_summary": str(OUT_ARTICLE_SUMMARY),
        "links": str(OUT_LINKS),
        "accessions": str(OUT_ACCESSIONS),
        "ena_audit": str(OUT_ENA_AUDIT),
        "n_accessions": len(accession_df),
        "n_project_accessions": len(project_accessions),
    })

    print("\nARTICLE SUMMARY")
    print(summary.to_string(index=False))

    print("\nACCESSION CANDIDATES")
    print(accession_df.to_string(index=False) if len(accession_df) else "No accessions found.")

    print("\nLINK CANDIDATES")
    print(links.head(80).to_string(index=False) if len(links) else "No candidate links found.")

    print("\nENA AUDIT")
    print(ena_audit.to_string(index=False) if len(ena_audit) else "No project accessions queried.")

if __name__ == "__main__":
    main()
