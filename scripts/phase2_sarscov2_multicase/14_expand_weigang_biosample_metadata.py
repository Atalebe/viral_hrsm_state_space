from pathlib import Path
import time
import urllib.parse
import urllib.request
import json
import xml.etree.ElementTree as ET
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

RUN_MANIFEST = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_run_manifest.csv"

OUT_BIOSAMPLE = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_biosample_metadata.csv"
OUT_JOINED = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_run_manifest_with_biosample_metadata.csv"
OUT_SUMMARY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_biosample_metadata_summary.csv"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "viral-hrsm-weigang-biosample-audit"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))

def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "viral-hrsm-weigang-biosample-audit"})
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read().decode("utf-8", errors="replace")

def esearch_biosample(accession):
    params = {
        "db": "biosample",
        "term": accession,
        "retmode": "json",
    }
    url = f"{EUTILS}/esearch.fcgi?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    ids = data.get("esearchresult", {}).get("idlist", [])
    return ids[0] if ids else ""

def efetch_biosample(uid):
    params = {
        "db": "biosample",
        "id": uid,
        "retmode": "xml",
    }
    url = f"{EUTILS}/efetch.fcgi?" + urllib.parse.urlencode(params)
    return fetch_text(url)

def parse_biosample_xml(accession, uid, xml_text):
    row = {
        "sample_accession": accession,
        "biosample_uid": uid,
        "biosample_accession_xml": "",
        "title": "",
        "organism": "",
        "taxonomy_id": "",
        "package": "",
        "model": "",
        "status": "parsed",
        "error": "",
    }

    attr_pairs = {}

    try:
        root = ET.fromstring(xml_text)
        biosample = root.find(".//BioSample")

        if biosample is None:
            row["status"] = "no_biosample_node"
            return row

        row["biosample_accession_xml"] = biosample.attrib.get("accession", "")
        row["package"] = biosample.attrib.get("package", "")
        row["model"] = biosample.attrib.get("model", "")

        title = biosample.find(".//Description/Title")
        if title is not None and title.text:
            row["title"] = title.text.strip()

        organism = biosample.find(".//Description/Organism")
        if organism is not None:
            row["organism"] = organism.attrib.get("taxonomy_name", "") or (organism.text or "")
            row["taxonomy_id"] = organism.attrib.get("taxonomy_id", "")

        for attr in biosample.findall(".//Attributes/Attribute"):
            name = attr.attrib.get("attribute_name") or attr.attrib.get("harmonized_name") or attr.attrib.get("display_name") or "unknown"
            value = (attr.text or "").strip()
            if name:
                attr_pairs[name] = value

        preferred = [
            "collection_date",
            "geo_loc_name",
            "host",
            "host_disease",
            "isolate",
            "isolation_source",
            "sample_type",
            "strain",
            "description",
            "host_age",
            "host_sex",
            "lat_lon",
            "passage_history",
            "collected_by",
            "purpose_of_sampling",
        ]

        for key in preferred:
            row[key] = attr_pairs.get(key, "")

        row["all_attributes"] = "|".join(f"{k}={v}" for k, v in sorted(attr_pairs.items()))

    except Exception as exc:
        row["status"] = "parse_failed"
        row["error"] = f"{type(exc).__name__}: {exc}"

    return row

def main():
    if not RUN_MANIFEST.exists():
        raise FileNotFoundError(f"Missing Weigang run manifest: {RUN_MANIFEST}")

    manifest = pd.read_csv(RUN_MANIFEST)
    samples = sorted(manifest["sample_accession"].dropna().astype(str).unique())

    rows = []

    for i, accession in enumerate(samples, start=1):
        print({"status": "fetching_biosample", "i": i, "n": len(samples), "accession": accession})
        uid = ""
        try:
            uid = esearch_biosample(accession)
            time.sleep(0.34)

            if not uid:
                rows.append({
                    "sample_accession": accession,
                    "biosample_uid": "",
                    "status": "no_uid_found",
                    "error": "",
                })
                continue

            xml_text = efetch_biosample(uid)
            time.sleep(0.34)

            rows.append(parse_biosample_xml(accession, uid, xml_text))

        except Exception as exc:
            rows.append({
                "sample_accession": accession,
                "biosample_uid": uid,
                "status": "fetch_failed",
                "error": f"{type(exc).__name__}: {exc}",
            })

    biosample = pd.DataFrame(rows)
    OUT_BIOSAMPLE.parent.mkdir(parents=True, exist_ok=True)
    biosample.to_csv(OUT_BIOSAMPLE, index=False)

    joined = manifest.merge(biosample, on="sample_accession", how="left", suffixes=("", "_biosample"))
    joined.to_csv(OUT_JOINED, index=False)

    def nonempty_count(col):
        if col not in joined.columns:
            return 0
        return int(joined[col].fillna("").astype(str).str.len().gt(0).sum())

    summary = pd.DataFrame([{
        "case_id": "WEIGANG_2021_ERP132087",
        "n_run_manifest_rows": len(manifest),
        "n_unique_samples": len(samples),
        "n_biosample_rows": len(biosample),
        "n_parsed": int(biosample.get("status", pd.Series(dtype=str)).eq("parsed").sum()),
        "n_collection_date": nonempty_count("collection_date"),
        "n_isolate": nonempty_count("isolate"),
        "n_strain": nonempty_count("strain"),
        "n_host": nonempty_count("host"),
        "n_host_disease": nonempty_count("host_disease"),
        "n_geo_loc_name": nonempty_count("geo_loc_name"),
        "next_required": "inspect sample titles and BioSample attributes for day/timepoint labels; compare to paper figure timeline",
    }])
    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "biosample_metadata": str(OUT_BIOSAMPLE),
        "joined_manifest": str(OUT_JOINED),
        "summary": str(OUT_SUMMARY),
        "n_samples": len(samples),
    })

    print(summary.to_string(index=False))

    preview_cols = [
        "sample_accession",
        "sample_title",
        "run_accession",
        "collection_date",
        "isolate",
        "strain",
        "host",
        "host_disease",
        "geo_loc_name",
        "title",
        "status",
        "all_attributes",
    ]
    preview_cols = [c for c in preview_cols if c in joined.columns]
    print(joined[preview_cols].to_string(index=False))

if __name__ == "__main__":
    main()
