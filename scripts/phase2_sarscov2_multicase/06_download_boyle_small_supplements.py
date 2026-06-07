from pathlib import Path
import urllib.request
import urllib.error
import zipfile
import pandas as pd
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]

LINK_AUDIT = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_supplement_link_audit.csv"

OUT_DIR = ROOT / "data" / "interim" / "phase2_sarscov2_multicase" / "boyle_supplements"
OUT_ZIP_INVENTORY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_supplement_zip_inventory.csv"
OUT_DOWNLOADS = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_supplement_downloads.csv"
OUT_TABLE_INVENTORY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_supplement_table_inventory.csv"

MAX_DOWNLOAD_BYTES = 20_000_000
TABLE_SUFFIXES = {".csv", ".tsv", ".txt", ".xlsx", ".xls"}

def safe_name(s):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(s))

def candidate_urls(url):
    urls = [url]

    # PMC sometimes serves binary files more reliably through ?download=1.
    if "pmc.ncbi.nlm.nih.gov" in url and "?" not in url:
        urls.append(url + "?download=1")

    # If a URL has a PMC article-instance binary route, keep it but also try HTTPS only.
    urls = list(dict.fromkeys(urls))
    return urls

def download(url, outpath):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept": "application/zip,application/octet-stream,*/*",
    }

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=120) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()

    if len(data) > MAX_DOWNLOAD_BYTES:
        raise RuntimeError(f"Downloaded file exceeds size cap: {len(data)} bytes")

    outpath.write_bytes(data)

    return {
        "bytes_downloaded": len(data),
        "content_type": content_type,
        "is_zip_signature": data[:4] == b"PK\x03\x04",
        "first_120_bytes": data[:120].decode("utf-8", errors="replace").replace("\n", " "),
    }

def inspect_table(path, extract_root):
    suffix = path.suffix.lower()
    rows = []

    preview_dir = extract_root / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)

    if suffix in {".xlsx", ".xls"}:
        xls = pd.ExcelFile(path)
        for sheet in xls.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet)
            preview = preview_dir / f"{path.stem}__{safe_name(sheet)}__preview.csv"
            df.head(30).to_csv(preview, index=False)
            rows.append({
                "file": str(path.relative_to(ROOT)),
                "sheet_name": sheet,
                "n_rows": len(df),
                "n_cols": len(df.columns),
                "columns": "|".join(map(str, df.columns)),
                "preview_csv": str(preview.relative_to(ROOT)),
            })

    elif suffix in {".csv", ".tsv", ".txt"}:
        sep = "\t" if suffix == ".tsv" else None
        try:
            df = pd.read_csv(path, sep=sep, engine="python")
        except Exception:
            df = pd.read_csv(path, sep="\t", engine="python")

        preview = preview_dir / f"{path.stem}__preview.csv"
        df.head(30).to_csv(preview, index=False)
        rows.append({
            "file": str(path.relative_to(ROOT)),
            "sheet_name": "",
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "columns": "|".join(map(str, df.columns)),
            "preview_csv": str(preview.relative_to(ROOT)),
        })

    return rows

def main():
    if not LINK_AUDIT.exists():
        raise FileNotFoundError(f"Missing supplement link audit: {LINK_AUDIT}")

    links = pd.read_csv(LINK_AUDIT)

    candidates = links[
        links["href"].astype(str).str.contains("viruses-17-01313-s001.zip", case=False, na=False)
    ].copy()

    if candidates.empty:
        raise RuntimeError("Could not find viruses-17-01313-s001.zip in supplement link audit.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    download_rows = []
    zip_rows = []
    table_rows = []

    for _, row in candidates.iterrows():
        original_url = row["href"]
        filename = Path(original_url.split("?")[0]).name
        local_zip = OUT_DIR / filename

        success_zip = False
        last_error = ""

        for url in candidate_urls(original_url):
            try:
                info = download(url, local_zip)

                record = {
                    "source_url": url,
                    "original_url": original_url,
                    "local_path": str(local_zip.relative_to(ROOT)),
                    "bytes_downloaded": info["bytes_downloaded"],
                    "content_type": info["content_type"],
                    "is_zip_signature": info["is_zip_signature"],
                    "first_120_bytes": info["first_120_bytes"],
                    "status": "downloaded",
                    "error": "",
                }

                if not info["is_zip_signature"]:
                    record["status"] = "downloaded_not_zip_payload"
                    download_rows.append(record)
                    last_error = "Downloaded payload did not have ZIP signature."
                    continue

                download_rows.append(record)
                success_zip = True
                break

            except urllib.error.HTTPError as exc:
                last_error = f"HTTPError {exc.code}: {exc.reason}"
                download_rows.append({
                    "source_url": url,
                    "original_url": original_url,
                    "local_path": str(local_zip.relative_to(ROOT)),
                    "bytes_downloaded": 0,
                    "content_type": "",
                    "is_zip_signature": False,
                    "first_120_bytes": "",
                    "status": "download_failed",
                    "error": last_error,
                })
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                download_rows.append({
                    "source_url": url,
                    "original_url": original_url,
                    "local_path": str(local_zip.relative_to(ROOT)),
                    "bytes_downloaded": 0,
                    "content_type": "",
                    "is_zip_signature": False,
                    "first_120_bytes": "",
                    "status": "download_failed",
                    "error": last_error,
                })

        if not success_zip:
            zip_rows.append({
                "zip_file": str(local_zip.relative_to(ROOT)),
                "member_name": "",
                "file_size": 0,
                "compress_size": 0,
                "suffix": "",
                "status": "not_a_zip_or_download_failed",
                "error": last_error,
            })
            continue

        extract_dir = OUT_DIR / local_zip.stem
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(local_zip, "r") as zf:
                members = zf.infolist()

                for m in members:
                    zip_rows.append({
                        "zip_file": str(local_zip.relative_to(ROOT)),
                        "member_name": m.filename,
                        "file_size": m.file_size,
                        "compress_size": m.compress_size,
                        "suffix": Path(m.filename).suffix.lower(),
                        "status": "zip_member",
                        "error": "",
                    })

                zf.extractall(extract_dir)

            for path in extract_dir.rglob("*"):
                if path.is_file() and path.suffix.lower() in TABLE_SUFFIXES:
                    table_rows.extend(inspect_table(path, extract_dir))

        except zipfile.BadZipFile as exc:
            zip_rows.append({
                "zip_file": str(local_zip.relative_to(ROOT)),
                "member_name": "",
                "file_size": 0,
                "compress_size": 0,
                "suffix": "",
                "status": "bad_zip_after_signature_check",
                "error": str(exc),
            })

    pd.DataFrame(download_rows).to_csv(OUT_DOWNLOADS, index=False)
    pd.DataFrame(zip_rows).to_csv(OUT_ZIP_INVENTORY, index=False)

    if table_rows:
        pd.DataFrame(table_rows).to_csv(OUT_TABLE_INVENTORY, index=False)
    else:
        pd.DataFrame(columns=[
            "file", "sheet_name", "n_rows", "n_cols", "columns", "preview_csv"
        ]).to_csv(OUT_TABLE_INVENTORY, index=False)

    print({
        "status": "wrote",
        "downloads": str(OUT_DOWNLOADS),
        "zip_inventory": str(OUT_ZIP_INVENTORY),
        "table_inventory": str(OUT_TABLE_INVENTORY),
        "n_download_rows": len(download_rows),
        "n_zip_rows": len(zip_rows),
        "n_tables": len(table_rows),
    })

    print("\nDOWNLOADS")
    print(pd.DataFrame(download_rows).to_string(index=False))

    print("\nZIP INVENTORY")
    print(pd.DataFrame(zip_rows).to_string(index=False))

    print("\nTABLE INVENTORY")
    if table_rows:
        print(pd.DataFrame(table_rows).to_string(index=False))
    else:
        print("No table-like files found.")

if __name__ == "__main__":
    main()
