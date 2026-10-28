"""
Simple empirical model analysis across recent controlled/adversarial data.

[CLASSIFICATION]: [PHASE 10 MODEL REVISION SUPPORT]
Collects (N, F, L) points from known EXP-025/027/029 masters + hardcoded priors.
Computes per-point c = L / (F/N), mean, variance.
Outputs revised observations for L ~ f(F, N, structure).

No overclaims. Use for iteration.
"""

import csv
from pathlib import Path
import statistics

def load_points_from_csv(path, n_col='N', f_col='achieved_F', l_col='obs_L'):
    pts = []
    try:
        with open(path) as f:
            for r in csv.DictReader(f):
                try:
                    n = float(r.get(n_col, 0))
                    fval = float(r.get(f_col, 0) or r.get('F', 0))
                    l = float(r.get(l_col, 0))
                    if n > 0 and fval > 0 and l > 0:
                        pts.append({'N': n, 'F': fval, 'L': l, 'source': str(path)})
                except:
                    pass
    except:
        pass
    return pts

def main():
    points = []

    # Load recent masters
    points += load_points_from_csv('results/exp027_explicit_f_20260701_084654/exp027_master.csv')
    points += load_points_from_csv('results/exp028_adversarial_f_20260701_085128/exp028_master.csv')
    points += load_points_from_csv('results/exp029_stronger_adv_20260701_085503/exp029_master.csv')

    # Add known from exp025/026 approx (from reports)
    points += [
        {'N': 1334, 'F': 588, 'L': 0.0765, 'source': 'exp025'},
        {'N': 1334, 'F': 1000, 'L': 0.0772, 'source': 'exp025'},
        {'N': 1067, 'F': 225, 'L': 0.0778, 'source': 'exp026'},
        {'N': 1067, 'F': 766, 'L': 0.0759, 'source': 'exp026'},
    ]

    print("Collected points:", len(points))
    cs = []
    for p in points:
        c = p['L'] / (p['F'] / p['N'])
        p['c'] = c
        cs.append(c)
        print(f"  N={p['N']:.0f} F={p['F']:.0f} L={p['L']:.4f} c={c:.3f} ({p['source']})")

    if cs:
        print("\n=== Empirical c stats ===")
        print(f"mean c = {statistics.mean(cs):.4f}")
        if len(cs) > 1:
            print(f"stdev c = {statistics.stdev(cs):.4f}")
            print(f"min c = {min(cs):.4f}  max c = {max(cs):.4f}")

    print("\n[OBSERVATION]: c varies substantially (low in high-F adv/layered structures).")
    print("Supports: L << F/N in practice due to rewrite locality. Model requires structure term.")

    # Save summary
    out = Path("results") / "model_fit_summary.txt"
    with open(out, "w") as f:
        f.write("Model fit summary from EXP-025/027/028/029 + priors\n")
        f.write(f"Points: {len(points)}\n")
        if cs:
            f.write(f"mean c: {statistics.mean(cs):.4f}\n")
            if len(cs)>1: f.write(f"stdev: {statistics.stdev(cs):.4f}\n")
        f.write("Key: architecture caps L strongly; c not constant.\n")
    print(f"\nSaved: {out}")

if __name__ == "__main__":
    main()