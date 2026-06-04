from pathlib import Path
import matplotlib.pyplot as plt


def plot_hrsm_scatter(df, x="H_v", y="M_v", label_col=None, outpath=None):
    fig, ax = plt.subplots(figsize=(6, 5))
    if label_col and label_col in df.columns:
        for label, sub in df.groupby(label_col):
            ax.scatter(sub[x], sub[y], label=str(label), alpha=0.8)
        ax.legend(frameon=False)
    else:
        ax.scatter(df[x], df[y], alpha=0.8)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f"Viral HRSM projection: {x} vs {y}")
    fig.tight_layout()
    if outpath:
        outpath = Path(outpath)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(outpath, dpi=300)
    return fig, ax
