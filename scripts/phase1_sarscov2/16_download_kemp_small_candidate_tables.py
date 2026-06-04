from pathlib import Path
import urllib.request
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[2]

CANDIDATES = ROOT / "metadata" / "kemp_github_hrsm_candidate_files.csv"
OUT_DIR = ROOT / "data" / "interim" / "kemp_github_small"
OUT_DOWNLOADS = ROOT / "metadata" / "kemp_downloaded_small_files.csv"
OUT_XLSX_INVENTORY = ROOT / "metadata" / "kemp_xlsx_sheet_inventory.csv"

MAX_BYTES = 5_000_000
ALLOWED_SUFFIXES = {".xlsx", ".xls", ".csv", ".tsv", ".txt", ".md"}

def safe_name(path):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", path.replace("/", "__"))

def download(url, outpath):
    req = urllib.request.Request(url, headers={"User-Agent": "viral-hrsm-small-file-audit"})
    with urllib.request.urlopen(req, timeout=90) as response:
        data = response.read()
    outpath.write_bytes(data)
    return len(data)

def inspect_xlsx(path):
    try:
        xls = pd.ExcelFile(path)
    except ImportError as e:
        raise RuntimeError(
            "Excel inspection requires openpyxl. Run: pip install openpyxl"
        ) from e

    rows = []
    preview_dir = OUT_DIR / "xlsx_previews"
    preview_dir.mkdir(parents=True, exist_ok=True)

    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        preview_path = preview_dir / f"{path.stem}__{safe_name(sheet)}__preview.csv"
        df.head(20).to_csv(preview_path, index=False)

        rows.append({
            "workbook": str(path.relative_to(ROOT)),
            "sheet_name": sheet,
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "columns": "|".join(map(str, df.columns)),
            "preview_csv": str(preview_path.relative_to(ROOT)),
        })

    return rows

def main():
    if not CANDIDATES.exists():
        raise FileNotFoundError(f"Missing candidate inventory: {CANDIDATES}")

    df = pd.read_csv(CANDIDATES)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    downloaded = []
    xlsx_rows = []

    for _, row in df.iterrows():
        suffix = str(row.get("suffix", "")).lower()
        size = int(row.get("size_bytes", 0))
        path = str(row.get("path", ""))
        raw_url = str(row.get("raw_url", ""))

        should_download = (
            suffix in ALLOWED_SUFFIXES
            and size <= MAX_BYTES
            and "large_file_do_not_download_initially" not in str(row.get("hrsm_tags", ""))
        )

        if not should_download:
            downloaded.append({
                "path": path,
                "downloaded": False,
                "reason": f"skipped suffix={suffix} size={size}",
                "local_path": "",
                "bytes_downloaded": 0,
            })
            continue

        local_path = OUT_DIR / safe_name(path)
        n_bytes = download(raw_url, local_path)

        downloaded.append({
            "path": path,
            "downloaded": True,
            "reason": "small_allowed_file",
            "local_path": str(local_path.relative_to(ROOT)),
            "bytes_downloaded": n_bytes,
        })

        if suffix in {".xlsx", ".xls"}:
            xlsx_rows.extend(inspect_xlsx(local_path))

    pd.DataFrame(downloaded).to_csv(OUT_DOWNLOADS, index=False)
    pd.DataFrame(xlsx_rows).to_csv(OUT_XLSX_INVENTORY, index=False)

    print({
        "status": "wrote",
        "downloads": str(OUT_DOWNLOADS),
        "xlsx_inventory": str(OUT_XLSX_INVENTORY),
        "downloaded_files": sum(1 for r in downloaded if r["downloaded"]),
        "xlsx_sheets": len(xlsx_rows),
    })

    print(pd.DataFrame(downloaded).to_string(index=False))

    if xlsx_rows:
        print(pd.DataFrame(xlsx_rows)[["sheet_name", "n_rows", "n_cols", "columns", "preview_csv"]].to_string(index=False))

if __name__ == "__main__":
    main()
