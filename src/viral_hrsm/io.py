from pathlib import Path
import pandas as pd
import yaml


def read_yaml(path):
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_table(path):
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".tsv", ".txt"}:
        return pd.read_csv(path, sep="\t")
    raise ValueError(f"Unsupported table format: {path.suffix}")


def write_table(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".csv":
        df.to_csv(path, index=False)
    elif path.suffix.lower() in {".tsv", ".txt"}:
        df.to_csv(path, sep="\t", index=False)
    else:
        raise ValueError(f"Unsupported table format: {path.suffix}")
