from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]

PROBS = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_probability_matrix_daily_collapsed.csv"
COUNTS = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_count_matrix_daily_collapsed.csv"

OUT_DIR = ROOT / "figures" / "phase1_sarscov2"
OUT_STATIONARY = ROOT / "metadata" / "kemp_fig5a_daily_collapsed_stationary_distribution.csv"
OUT_SUMMARY = ROOT / "metadata" / "kemp_fig5a_transition_heatmap_summary.csv"

def stationary_distribution_linear(P):
    """
    Solve pi P = pi with sum(pi)=1.

    This is safer than power iteration for periodic chains, including
    deterministic two-state cycles.
    """
    P = np.asarray(P, dtype=float)
    n = P.shape[0]

    # Fix dangling rows, although this matrix should not have them.
    P = P.copy()
    for i in range(n):
        if np.isclose(P[i].sum(), 0):
            P[i, i] = 1.0

    A = P.T - np.eye(n)
    A[-1, :] = 1.0

    b = np.zeros(n)
    b[-1] = 1.0

    pi = np.linalg.solve(A, b)
    pi[np.abs(pi) < 1e-12] = 0.0
    pi = pi / pi.sum()
    return pi

def main():
    if not PROBS.exists():
        raise FileNotFoundError(f"Missing daily-collapsed probability matrix: {PROBS}")

    probs = pd.read_csv(PROBS, index_col=0)
    counts = pd.read_csv(COUNTS, index_col=0) if COUNTS.exists() else None

    states = list(probs.index)
    P = probs.to_numpy(dtype=float)

    pi = stationary_distribution_linear(P)
    stationary = pd.DataFrame({
        "state": states,
        "stationary_probability": pi,
    }).sort_values("stationary_probability", ascending=False)

    OUT_STATIONARY.parent.mkdir(parents=True, exist_ok=True)
    stationary.to_csv(OUT_STATIONARY, index=False)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    heatmap_path = OUT_DIR / "kemp_fig5a_daily_collapsed_transition_heatmap.png"
    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(P, aspect="auto")

    ax.set_xticks(range(len(states)))
    ax.set_yticks(range(len(states)))
    ax.set_xticklabels(states, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(states, fontsize=8)

    ax.set_xlabel("To state")
    ax.set_ylabel("From state")
    ax.set_title("Kemp Fig. 5a daily-collapsed transition probability matrix")

    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            ax.text(j, i, f"{P[i, j]:.2f}", ha="center", va="center", fontsize=8)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Transition probability")
    fig.tight_layout()
    fig.savefig(heatmap_path, dpi=300)
    plt.close(fig)

    stationary_path = OUT_DIR / "kemp_fig5a_daily_collapsed_stationary_distribution.png"
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(stationary["state"], stationary["stationary_probability"])
    ax.set_ylabel("Stationary probability")
    ax.set_xlabel("State")
    ax.set_title("Stationary distribution, daily-collapsed transition matrix")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(stationary_path, dpi=300)
    plt.close(fig)

    summary = pd.DataFrame([
        {
            "output": str(heatmap_path.relative_to(ROOT)),
            "description": "Heatmap of daily-collapsed transition probabilities."
        },
        {
            "output": str(stationary_path.relative_to(ROOT)),
            "description": "Stationary distribution from linear stationary-equation solve."
        },
        {
            "output": str(OUT_STATIONARY.relative_to(ROOT)),
            "description": "Stationary distribution table."
        }
    ])
    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "heatmap": str(heatmap_path),
        "stationary_plot": str(stationary_path),
        "stationary_table": str(OUT_STATIONARY),
        "summary": str(OUT_SUMMARY),
        "stationary_solver": "linear_system_piP_equals_pi",
    })

    print("\nPROBABILITY MATRIX")
    print(probs.to_string())

    print("\nSTATIONARY DISTRIBUTION")
    print(stationary.to_string(index=False))

    if counts is not None:
        print("\nCOUNT MATRIX")
        print(counts.to_string())

if __name__ == "__main__":
    main()
