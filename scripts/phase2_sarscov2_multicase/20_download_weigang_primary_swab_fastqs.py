from pathlib import Path
import urllib.request
import pandas as pd
import hashlib
import time

ROOT = Path(__file__).resolve().parents[2]

PLAN = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_primary_swab_download_plan.csv"
PROTOCOL_AUDIT = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_raw_feature_protocol_audit.csv"

OUT_LOG = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_primary_swab_fastq_download_log.csv"

MAX_BYTES_PER_FILE = 2_000_000_000

def sha256_file(path, chunk_size=1024 * 1024):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def download(url, outpath):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "viral-hrsm-weigang-controlled-download"}
    )
    with urllib.request.urlopen(req, timeout=300) as response:
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_BYTES_PER_FILE:
            raise RuntimeError(f"Refusing file larger than cap: {content_length} bytes")

        outpath.parent.mkdir(parents=True, exist_ok=True)

        tmp = outpath.with_suffix(outpath.suffix + ".part")
        n = 0
        with response as r, tmp.open("wb") as f:
            while True:
                chunk = r.read(1024 * 1024)
                if not chunk:
                    break
                n += len(chunk)
                if n > MAX_BYTES_PER_FILE:
                    raise RuntimeError(f"Refusing file larger than cap after streaming: {n} bytes")
                f.write(chunk)

        tmp.rename(outpath)
        return n

def main():
    if not PLAN.exists():
        raise FileNotFoundError(f"Missing download plan: {PLAN}")
    if not PROTOCOL_AUDIT.exists():
        raise FileNotFoundError(f"Missing protocol audit: {PROTOCOL_AUDIT}")

    audit = pd.read_csv(PROTOCOL_AUDIT)
    if audit.empty or not bool(audit.iloc[0]["protocol_ok"]):
        raise RuntimeError("Protocol audit has not passed. Refusing raw download.")

    plan = pd.read_csv(PLAN)
    plan = plan.sort_values(["sample_day", "timepoint_order", "file_index"]).reset_index(drop=True)

    rows = []

    for _, row in plan.iterrows():
        url = row["download_url"]
        local_dir = ROOT / row["planned_local_dir"]
        filename = Path(url).name
        outpath = local_dir / filename

        record = row.to_dict()
        record["local_path"] = str(outpath.relative_to(ROOT))
        record["download_attempted_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

        if outpath.exists() and outpath.stat().st_size > 0:
            record["status"] = "exists"
            record["bytes_downloaded"] = outpath.stat().st_size
            record["sha256"] = sha256_file(outpath)
            rows.append(record)
            print({"status": "exists", "file": str(outpath)})
            continue

        try:
            print({"status": "downloading", "url": url, "out": str(outpath)})
            n = download(url, outpath)
            record["status"] = "downloaded"
            record["bytes_downloaded"] = n
            record["sha256"] = sha256_file(outpath)
        except Exception as exc:
            record["status"] = "failed"
            record["bytes_downloaded"] = 0
            record["sha256"] = ""
            record["error"] = f"{type(exc).__name__}: {exc}"

        rows.append(record)

        pd.DataFrame(rows).to_csv(OUT_LOG, index=False)

    out = pd.DataFrame(rows)
    OUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_LOG, index=False)

    print({
        "status": "wrote",
        "download_log": str(OUT_LOG),
        "n_files": len(out),
        "n_downloaded_or_exists": int(out["status"].isin(["downloaded", "exists"]).sum()),
        "n_failed": int(out["status"].eq("failed").sum()),
        "total_bytes": int(out["bytes_downloaded"].sum()),
    })

    print(out[[
        "sample_day",
        "run_accession",
        "file_index",
        "local_path",
        "status",
        "bytes_downloaded",
        "sha256",
    ]].to_string(index=False))

if __name__ == "__main__":
    main()
