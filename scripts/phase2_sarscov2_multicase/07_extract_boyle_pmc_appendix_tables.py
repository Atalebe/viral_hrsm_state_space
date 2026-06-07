from pathlib import Path
import re
import urllib.request
import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]

PMC_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC12567731/"

OUT_DIR = ROOT / "metadata" / "phase2_sarscov2_multicase"
OUT_TEXT = OUT_DIR / "boyle_pmc_appendix_text.txt"
OUT_TABLES = OUT_DIR / "boyle_pmc_appendix_tables_inventory.csv"
OUT_LINKED_TABLES = OUT_DIR / "boyle_pmc_linked_tables_inventory.csv"
OUT_LC_HITS = OUT_DIR / "boyle_pmc_lc_sample_hits.csv"

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

def clean_text(s):
    return re.sub(r"\s+", " ", str(s)).strip()

def table_to_dataframe(table):
    rows = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        rows.append([clean_text(c.get_text(" ", strip=True)) for c in cells])

    if not rows:
        return pd.DataFrame()

    max_len = max(len(r) for r in rows)
    rows = [r + [""] * (max_len - len(r)) for r in rows]

    # If first row looks like header, use it.
    header = rows[0]
    body = rows[1:] if len(rows) > 1 else []

    if body and any(h for h in header):
        return pd.DataFrame(body, columns=header)

    return pd.DataFrame(rows)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print({"status": "fetching", "url": PMC_URL})
    html = fetch(PMC_URL)
    soup = BeautifulSoup(html, "html.parser")

    appendix = soup.find(id="app1-viruses-17-01313")
    if appendix is None:
        # fallback: find any appendix-ish section
        appendix = soup.find(id=re.compile(r"app1|supplement", re.I))

    if appendix is None:
        raise RuntimeError("Could not find appendix/supplement section in PMC page.")

    appendix_text = appendix.get_text("\n", strip=True)
    OUT_TEXT.write_text(appendix_text, encoding="utf-8")

    # Extract LC sample IDs from appendix and entire page.
    full_text = soup.get_text("\n", strip=True)
    lc_hits = sorted(set(re.findall(r"\bLC-\d+\b", full_text)))
    lc_rows = [{"sample_title": x, "source": "pmc_full_text"} for x in lc_hits]
    pd.DataFrame(lc_rows).to_csv(OUT_LC_HITS, index=False)

    table_rows = []
    table_dir = OUT_DIR / "boyle_pmc_appendix_tables"
    table_dir.mkdir(parents=True, exist_ok=True)

    # Tables inside appendix.
    for i, table in enumerate(appendix.find_all("table"), start=1):
        df = table_to_dataframe(table)
        out_csv = table_dir / f"appendix_table_{i}.csv"
        df.to_csv(out_csv, index=False)

        table_rows.append({
            "table_scope": "appendix",
            "table_index": i,
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "columns": "|".join(map(str, df.columns)),
            "csv_path": str(out_csv.relative_to(ROOT)),
            "contains_lc_sample_ids": df.astype(str).apply(lambda col: col.str.contains(r"LC-\d+", regex=True, na=False)).any().any() if len(df) else False,
        })

    pd.DataFrame(table_rows).to_csv(OUT_TABLES, index=False)

    # Also extract the normal article tables accessible by /table/... links from the PMC page.
    linked_rows = []
    linked_dir = OUT_DIR / "boyle_pmc_linked_tables"
    linked_dir.mkdir(parents=True, exist_ok=True)

    table_links = []
    for a in soup.find_all("a"):
        href = a.get("href") or ""
        if "/table/" in href:
            table_links.append(urllib.request.urljoin(PMC_URL, href))

    table_links = list(dict.fromkeys(table_links))

    for i, url in enumerate(table_links, start=1):
        try:
            table_html = fetch(url)
            table_soup = BeautifulSoup(table_html, "html.parser")
            table = table_soup.find("table")
            if table is None:
                continue

            df = table_to_dataframe(table)
            out_csv = linked_dir / f"linked_table_{i}.csv"
            df.to_csv(out_csv, index=False)

            linked_rows.append({
                "source_url": url,
                "table_index": i,
                "n_rows": len(df),
                "n_cols": len(df.columns),
                "columns": "|".join(map(str, df.columns)),
                "csv_path": str(out_csv.relative_to(ROOT)),
                "contains_lc_sample_ids": df.astype(str).apply(lambda col: col.str.contains(r"LC-\d+", regex=True, na=False)).any().any() if len(df) else False,
            })
        except Exception as exc:
            linked_rows.append({
                "source_url": url,
                "table_index": i,
                "n_rows": 0,
                "n_cols": 0,
                "columns": "",
                "csv_path": "",
                "contains_lc_sample_ids": False,
                "error": f"{type(exc).__name__}: {exc}",
            })

    pd.DataFrame(linked_rows).to_csv(OUT_LINKED_TABLES, index=False)

    print({
        "status": "wrote",
        "appendix_text": str(OUT_TEXT),
        "appendix_tables": str(OUT_TABLES),
        "linked_tables": str(OUT_LINKED_TABLES),
        "lc_hits": str(OUT_LC_HITS),
        "n_lc_hits": len(lc_hits),
        "n_appendix_tables": len(table_rows),
        "n_linked_tables": len(linked_rows),
    })

    print("\nLC SAMPLE HITS")
    if lc_rows:
        print(pd.DataFrame(lc_rows).head(80).to_string(index=False))
    else:
        print("No LC sample IDs found in PMC full text.")

    print("\nAPPENDIX TABLES")
    print(pd.DataFrame(table_rows).to_string(index=False) if table_rows else "No appendix tables found.")

    print("\nLINKED TABLES")
    print(pd.DataFrame(linked_rows).to_string(index=False) if linked_rows else "No linked tables found.")

if __name__ == "__main__":
    main()
