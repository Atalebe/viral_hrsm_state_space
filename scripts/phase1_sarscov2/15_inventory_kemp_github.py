from pathlib import Path
import urllib.request
import json
import pandas as pd
from datetime import date

ROOT = Path(__file__).resolve().parents[2]

OWNER = "Steven-Kemp"
REPO = "sequence_files"

OUT_INVENTORY = ROOT / "metadata" / "kemp_github_sequence_files_inventory.csv"
OUT_CANDIDATES = ROOT / "metadata" / "kemp_github_hrsm_candidate_files.csv"
OUT_SUMMARY = ROOT / "metadata" / "kemp_github_inventory_summary.md"

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "viral-hrsm-metadata-audit"
        }
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))

def classify_file(path, size):
    p = path.lower()
    ext = Path(path).suffix.lower()

    tags = []

    if ext in {".csv", ".tsv", ".txt", ".xlsx", ".xls"}:
        tags.append("table_like")
    if ext in {".fa", ".fasta", ".fna", ".aln"}:
        tags.append("sequence_like")
    if ext in {".fastq", ".fq", ".gz", ".bam", ".sam"}:
        tags.append("read_or_alignment_like")
    if "variant" in p or "mutation" in p or "freq" in p or "frequency" in p:
        tags.append("variant_frequency_candidate")
    if "fig" in p or "figure" in p or "source" in p:
        tags.append("figure_source_candidate")
    if "day" in p or "time" in p or "sample" in p:
        tags.append("sample_time_mapping_candidate")
    if "ct" in p or "viral" in p or "load" in p:
        tags.append("abundance_proxy_candidate")
    if "spike" in p or "d796h" in p or "h69" in p or "v70" in p:
        tags.append("escape_genotype_candidate")

    if not tags:
        tags.append("unclassified")

    if size is not None:
        try:
            if int(size) > 200_000_000:
                tags.append("large_file_do_not_download_initially")
        except Exception:
            pass

    return ";".join(tags)

def raw_url_for(branch, path):
    return f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{branch}/{path}"

def main():
    repo_url = f"https://api.github.com/repos/{OWNER}/{REPO}"
    print({"status": "fetching_repo_metadata", "url": repo_url})

    repo_meta = fetch_json(repo_url)
    default_branch = repo_meta.get("default_branch", "master")

    tree_url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{default_branch}?recursive=1"
    print({"status": "fetching_tree", "url": tree_url})

    tree = fetch_json(tree_url)
    items = tree.get("tree", [])

    rows = []
    for item in items:
        path = item.get("path")
        typ = item.get("type")
        size = item.get("size", None)

        if typ != "blob":
            continue

        rows.append({
            "repo": f"{OWNER}/{REPO}",
            "default_branch": default_branch,
            "path": path,
            "filename": Path(path).name,
            "suffix": Path(path).suffix.lower(),
            "size_bytes": size,
            "github_blob_url": item.get("url"),
            "raw_url": raw_url_for(default_branch, path),
            "hrsm_tags": classify_file(path, size),
        })

    df = pd.DataFrame(rows)
    OUT_INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_INVENTORY, index=False)

    if len(df):
        candidate_mask = df["hrsm_tags"].str.contains(
            "table_like|variant_frequency_candidate|figure_source_candidate|sample_time_mapping_candidate|abundance_proxy_candidate|escape_genotype_candidate",
            regex=True,
            na=False
        )
        candidates = df[candidate_mask].copy()
    else:
        candidates = pd.DataFrame(columns=df.columns)

    candidates.to_csv(OUT_CANDIDATES, index=False)

    md = []
    md.append("# Kemp GitHub Repository Inventory")
    md.append("")
    md.append(f"Generated: {date.today().isoformat()}")
    md.append("")
    md.append(f"Repository: `{OWNER}/{REPO}`")
    md.append(f"Default branch: `{default_branch}`")
    md.append("")
    md.append("## Inventory result")
    md.append("")
    md.append(f"- Total files: {len(df)}")
    md.append(f"- HRSM candidate files: {len(candidates)}")
    md.append("")
    md.append("## Candidate-file logic")
    md.append("")
    md.append("Files are flagged when names suggest tables, variant frequencies, figure-source data, sample-time mapping, abundance proxies, or escape-genotype information.")
    md.append("")
    md.append("## Next step")
    md.append("")
    md.append("Inspect candidate file names first. Download only small table-like files in the next step. Do not download large read, alignment, or compressed files until file sizes and sample mapping are clear.")
    md.append("")

    if len(candidates):
        md.append("## Top candidate files")
        md.append("")
        for _, row in candidates.head(30).iterrows():
            md.append(f"- `{row['path']}` [{row['hrsm_tags']}], size={row['size_bytes']}")
        md.append("")

    OUT_SUMMARY.write_text("\n".join(md), encoding="utf-8")

    print({
        "status": "wrote",
        "inventory": str(OUT_INVENTORY),
        "candidates": str(OUT_CANDIDATES),
        "summary": str(OUT_SUMMARY),
        "n_files": len(df),
        "n_candidates": len(candidates),
    })

    if len(candidates):
        print(candidates[["path", "size_bytes", "hrsm_tags"]].head(50).to_string(index=False))
    else:
        print("No HRSM candidate files found by filename heuristic.")

if __name__ == "__main__":
    main()
