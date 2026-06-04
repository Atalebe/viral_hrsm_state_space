import numpy as np
import pandas as pd
from scipy.stats import norm

def verify_memory_utility(csv_path):
    df = pd.read_csv(csv_path)
    
    # Target: Predict total structural velocity from state vectors
    y = df['velocity_norm_calendar_total'].dropna()
    idx = y.index
    
    # Model 1: Current State Only (Markovian Base: Heterogeneity, Resistance, Swarm)
    X_markov = df.loc[idx, ['H_v', 'R_v', 'S_v']]
    # Simple pseudo-inverse projection for mapping
    w_m = np.linalg.pinv(X_markov) @ y
    pred_m = X_markov @ w_m
    rss_m = np.sum((y - pred_m)**2)
    
    # Model 2: Complete Homeostatic Space (Non-Markovian: Includes Evolutionary Memory M_v)
    X_non_markov = df.loc[idx, ['H_v', 'R_v', 'S_v', 'M_v']]
    w_nm = np.linalg.pinv(X_non_markov) @ y
    pred_nm = X_non_markov @ w_nm
    rss_nm = np.sum((y - pred_nm)**2)
    
    # Output metrics
    print(f"--- Pipeline Memory Validation Summary ---")
    print(f"Markovian Core Residual Sum of Squares (RSS): {rss_m:.4f}")
    print(f"Non-Markovian RSS (With Memory Kernel):       {rss_nm:.4f}")
    print(f"Absolute Variance Variance Reduction:          {((rss_m - rss_nm) / rss_m)*100:.2f}%")

if __name__ == "__main__":
    verify_memory_utility("results/phase1_sarscov2/kemp_fig5a_phase_velocity.csv")
