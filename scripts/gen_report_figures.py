"""Generate publication-quality figures for the PredictIQ technical report and evaluation specifications.

Produces:
1. predicted_vs_actual.png: Scatter plot of predicted effort vs actual effort with source color coding.
2. per_source_error.png: Bar chart of cross-validation MdAPE by empirical source with macro/pooled baselines.
3. calibration_by_k.png: Empirical Bayes shrinkage curve and accuracy gain as a function of sample size k.
4. dataset_composition.png: Composition of the 915-project corpus by empirical source.
5. fitted_curve.png: Univariate power-law curve with conformal prediction intervals and data scatter.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Color Palette
PALETTE = {
    "primary": "#1E3A8A",      # Deep navy
    "secondary": "#2563EB",    # Vivid blue
    "accent": "#0D9488",       # Teal
    "highlight": "#D97706",    # Amber
    "danger": "#DC2626",       # Red
    "muted": "#64748B",        # Slate
    "light": "#F8FAFC",        # Off white
    "dark": "#0F172A",         # Near black
    "sources": {
        "china": "#2563EB",
        "kitchenham": "#0D9488",
        "att_aptness": "#7C3AED",
        "desharnais": "#EA580C",
        "maxwell": "#059669",
        "albrecht": "#DB2777",
    }
}

SOURCE_NAMES = {
    "china": "China (N=499)",
    "kitchenham": "Kitchenham (N=145)",
    "att_aptness": "AT&T Aptness (N=104)",
    "desharnais": "Desharnais (N=81)",
    "maxwell": "Maxwell (N=62)",
    "albrecht": "Albrecht (N=24)",
}


def load_dataset(repo_root: Path) -> pd.DataFrame:
    csv_path = repo_root / "backend" / "ml" / "data" / "projects_v2.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}")
    df = pd.read_csv(csv_path)
    if "size_value" in df.columns and "size_fp" not in df.columns:
        df["size_fp"] = df["size_value"]
    return df


def load_model_report(repo_root: Path) -> Dict[str, Any]:
    report_path = repo_root / "backend" / "ml" / "reports" / "model_report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"Model report not found at {report_path}")
    with open(report_path, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_predicted_vs_actual(df: pd.DataFrame, out_path: Path, a: float = 24.240774, b: float = 0.827027) -> None:
    """Plot actual effort vs predicted effort on log-log scale with source differentiation."""
    plt.figure(figsize=(8, 6.5), dpi=150)
    
    # Calculate predicted effort
    df = df.copy()
    df["pred_effort"] = a * (df["size_fp"] ** b)
    
    # Plot points by source
    for source, group in df.groupby("source"):
        color = PALETTE["sources"].get(str(source), PALETTE["muted"])
        label = SOURCE_NAMES.get(str(source), str(source).title())
        plt.scatter(
            group["size_fp"],
            group["effort_hours"],
            color=color,
            alpha=0.6,
            s=28,
            label=label,
            edgecolors="none",
        )
    
    # Identity line and factor of 2 lines
    s_grid = np.geomspace(df["size_fp"].min(), df["size_fp"].max(), 200)
    pred_grid = a * (s_grid ** b)
    
    plt.plot(s_grid, pred_grid, color="#1E293B", linewidth=2.0, label="Power-Law Fit (P50)")
    plt.plot(s_grid, pred_grid * 2.0, color="#94A3B8", linestyle="--", linewidth=1.2, label="Factor of 2 Band")
    plt.plot(s_grid, pred_grid * 0.5, color="#94A3B8", linestyle="--", linewidth=1.2)
    
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Functional Size (IFPUG Function Points)", fontsize=11, fontweight="medium")
    plt.ylabel("Actual Effort (Person-Hours)", fontsize=11, fontweight="medium")
    plt.title("Software Effort Estimation: Actual Effort vs Functional Size", fontsize=12, fontweight="bold", pad=12)
    plt.grid(True, which="both", linestyle=":", alpha=0.5, color="#CBD5E1")
    plt.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0", fontsize=9, loc="upper left")
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Generated: {out_path}")


def plot_per_source_error(report_data: Dict[str, Any], out_path: Path) -> None:
    """Plot cross-validation MdAPE across empirical repositories with macro/pooled baselines."""
    sources_data = report_data.get("per_source_breakdown", {})
    sources = ["albrecht", "att_aptness", "china", "desharnais", "kitchenham", "maxwell"]
    
    names = [s.replace("_", " ").title() for s in sources]
    mdapes = [sources_data[s]["mdape"] for s in sources]
    macro_mdape = report_data["summary"]["macro_mdape"]
    pooled_mdape = report_data["summary"]["pooled_mdape"]
    floor_mdape = 65.0
    
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=150)
    
    colors = [PALETTE["sources"].get(s, PALETTE["secondary"]) for s in sources]
    bars = ax.bar(names, mdapes, color=colors, width=0.55, edgecolor="#0F172A", linewidth=0.8, alpha=0.85)
    
    # Reference lines
    ax.axhline(macro_mdape, color="#2563EB", linestyle="--", linewidth=1.8, label=f"Macro Average LOSO: {macro_mdape:.1f}%")
    ax.axhline(pooled_mdape, color="#0D9488", linestyle="-.", linewidth=1.8, label=f"Pooled Overall: {pooled_mdape:.1f}%")
    ax.axhline(floor_mdape, color="#DC2626", linestyle=":", linewidth=2.0, label=f"Quality Floor Ceiling: {floor_mdape:.1f}%")
    
    # Value annotations on bars
    for bar, val in zip(bars, mdapes):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 1.2,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#1E293B"
        )
    
    ax.set_ylim(0, 80)
    ax.set_ylabel("Median Absolute Percentage Error (MdAPE %)", fontsize=11, fontweight="medium")
    ax.set_title("Leave-One-Source-Out (LOSO) Cross-Validation Accuracy by Dataset", fontsize=12, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle=":", alpha=0.6, color="#CBD5E1")
    ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0", fontsize=9.5, loc="upper right")
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Generated: {out_path}")


def plot_calibration_by_k(out_path: Path) -> None:
    """Plot Empirical Bayes shrinkage factor and relative MdAPE gain as sample size k increases."""
    prior_ratio = 2.83
    k_vals = np.linspace(0, 15, 100)
    w_vals = k_vals / (k_vals + prior_ratio)
    
    # Empirical measured points from evaluation: k=3: 11.9%, k=5: 14.9%, k=10: 19.5%
    k_points = [0, 1, 3, 5, 7, 10, 12, 15]
    # Modeled gain curve saturating near 22%
    gain_curve = 22.5 * (k_vals / (k_vals + 2.5))
    
    fig, ax1 = plt.subplots(figsize=(8, 5.2), dpi=150)
    
    color1 = "#1E3A8A"
    ax1.set_xlabel("Organization Historical Completed Projects (k)", fontsize=11, fontweight="medium")
    ax1.set_ylabel("Shrinkage Weight w(k) to Local Velocity", color=color1, fontsize=11, fontweight="medium")
    line1 = ax1.plot(k_vals, w_vals, color=color1, linewidth=2.2, label="Shrinkage Weight w(k) = k / (k + 2.83)")
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(-0.02, 1.0)
    ax1.grid(True, linestyle=":", alpha=0.5, color="#CBD5E1")
    
    ax2 = ax1.twinx()
    color2 = "#0D9488"
    ax2.set_ylabel("Relative MdAPE Accuracy Gain (%)", color=color2, fontsize=11, fontweight="medium")
    line2 = ax2.plot(k_vals, gain_curve, color=color2, linestyle="--", linewidth=2.0, label="Modeled Accuracy Gain (%)")
    
    # Measured anchor points
    measured_k = [3, 5, 10]
    measured_gains = [11.9, 14.9, 19.5]
    ax2.scatter(measured_k, measured_gains, color="#D97706", s=65, zorder=5, label="Empirical Cross-Val Points")
    for k, g in zip(measured_k, measured_gains):
        ax2.annotate(
            f"+{g:.1f}% (k={k})",
            (k, g),
            textcoords="offset points",
            xytext=(0, 9),
            ha="center",
            fontsize=9,
            fontweight="bold",
            color="#92400E"
        )
    
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(0, 26)
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines] + ["Empirical Measured Points"]
    
    plt.title("Organizational Calibration: Shrinkage Weight & Accuracy Improvement", fontsize=12, fontweight="bold", pad=12)
    fig.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Generated: {out_path}")


def plot_dataset_composition(df: pd.DataFrame, out_path: Path) -> None:
    """Plot dataset composition donut chart across empirical repositories."""
    source_counts = df["source"].value_counts()
    sources = ["china", "kitchenham", "att_aptness", "desharnais", "maxwell", "albrecht"]
    counts = [source_counts.get(s, 0) for s in sources]
    labels = [SOURCE_NAMES.get(s, s) for s in sources]
    colors = [PALETTE["sources"].get(s, PALETTE["muted"]) for s in sources]
    
    fig, ax = plt.subplots(figsize=(7.5, 6), dpi=150)
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=labels,
        autopct="%1.1f%%",
        pctdistance=0.75,
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
    )
    
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(9.5)
        
    for text in texts:
        text.set_fontsize(9.5)
        text.set_color("#1E293B")
        
    ax.set_title("Empirical Dataset Composition (Total N = 915 Projects)", fontsize=12, fontweight="bold", pad=15)
    
    # Center text
    ax.text(0, 0, "915 Projects\n100% IFPUG FP\n6 Sources", ha="center", va="center", fontsize=11, fontweight="bold", color="#1E3A8A")
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Generated: {out_path}")


def plot_fitted_curve(df: pd.DataFrame, out_path: Path, a: float = 24.240774, b: float = 0.827027) -> None:
    """Plot fitted power law curve with Mondrian conformal prediction interval bands."""
    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=150)
    
    # Scatter data
    ax.scatter(
        df["size_fp"],
        df["effort_hours"],
        color="#64748B",
        alpha=0.35,
        s=20,
        label="Empirical Observations (N=915)",
        edgecolors="none",
    )
    
    s_grid = np.geomspace(10, 4000, 300)
    p50_grid = a * (s_grid ** b)
    
    # Conformal bands (using medium bucket approximations for smooth visual band)
    q80 = 1.0053  # overall conformal 80 quantile in log space
    q50 = 0.6004  # overall conformal 50 quantile in log space
    
    p10_grid = p50_grid * np.exp(-q80)
    p90_grid = p50_grid * np.exp(q80)
    p25_grid = p50_grid * np.exp(-q50)
    p75_grid = p50_grid * np.exp(q50)
    
    # Fill bands
    ax.fill_between(s_grid, p10_grid, p90_grid, color="#93C5FD", alpha=0.35, label="80% Plausible Range (P10 - P90)")
    ax.fill_between(s_grid, p25_grid, p75_grid, color="#3B82F6", alpha=0.35, label="50% Likely Band (P25 - P75)")
    
    # Plot P50 line
    ax.plot(s_grid, p50_grid, color="#1E3A8A", linewidth=2.5, label=f"Monotone Power-Law: E = {a:.2f} · S^{b:.3f}")
    
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Functional Size (IFPUG Function Points)", fontsize=11, fontweight="medium")
    ax.set_ylabel("Engineering Effort (Person-Hours)", fontsize=11, fontweight="medium")
    ax.set_title("Monotone Power-Law Fit with Conformal Uncertainty Bands", fontsize=12, fontweight="bold", pad=12)
    ax.grid(True, which="both", linestyle=":", alpha=0.5, color="#CBD5E1")
    ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0", fontsize=9.5, loc="upper left")
    
    # Inset linear plot for early regime
    ax_inset = fig.add_axes([0.60, 0.20, 0.28, 0.28])
    s_linear = np.linspace(10, 500, 100)
    p50_linear = a * (s_linear ** b)
    ax_inset.plot(s_linear, p50_linear, color="#1E3A8A", linewidth=2)
    mask = (df["size_fp"] <= 500) & (df["effort_hours"] <= 15000)
    ax_inset.scatter(df.loc[mask, "size_fp"], df.loc[mask, "effort_hours"], color="#64748B", alpha=0.3, s=10)
    ax_inset.set_title("Linear Scale (<= 500 FP)", fontsize=8.5, fontweight="bold")
    ax_inset.set_xlabel("Size (FP)", fontsize=7.5)
    ax_inset.set_ylabel("Effort (Hrs)", fontsize=7.5)
    ax_inset.tick_params(labelsize=7)
    ax_inset.grid(True, linestyle=":", alpha=0.4)
    
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Generated: {out_path}")


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    figures_dir = repo_root / "docs" / "report" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    df = load_dataset(repo_root)
    report_data = load_model_report(repo_root)
    
    plot_predicted_vs_actual(df, figures_dir / "predicted_vs_actual.png")
    plot_per_source_error(report_data, figures_dir / "per_source_error.png")
    plot_calibration_by_k(figures_dir / "calibration_by_k.png")
    plot_dataset_composition(df, figures_dir / "dataset_composition.png")
    plot_fitted_curve(df, figures_dir / "fitted_curve.png")
    
    print("\nAll 5 report figures generated successfully in docs/report/figures/.")


if __name__ == "__main__":
    main()
