"""
05_figures.py  -  Article figures, drawn only from the CSV files in results/.

  results/ige-single-vs-average.png   single-year vs three-year-average IGE
  results/ige-by-age.png              IGE by the child's age when earnings are measured
  results/one-bad-year.png            what PSID's $1 bottom code does to each measure

Run from the post6 folder:  python code/05_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"

# Palette checked with a colour-vision-deficiency validator (all checks pass)
COLOR = {"daughters": "#00897a", "sons": "#c4572a", "all children": "#5b6770"}
LABEL = {"daughters": "Daughters", "sons": "Sons", "all children": "All children"}
INK, MUTED, GRID = "#1f2a28", "#5f6b67", "#e4e7e3"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "text.parse_math": False, "savefig.bbox": "tight", "savefig.facecolor": "white",
})


def finish(ax, title, subtitle):
    ax.set_title(title, loc="left", fontsize=13.5, fontweight="bold", pad=26)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=10, color=MUTED, va="bottom")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
# Figure 1. Single year vs three-year averages, with 95% intervals
# ---------------------------------------------------------------------------
r = pd.read_csv(RES / "ige_results.csv")
r = r[r["spec"].isin(["Single year", "Three-year averages"])]
fig, ax = plt.subplots(figsize=(8, 4.6))
groups = ["daughters", "sons", "all children"]
for i, g in enumerate(groups):
    for j, (spec, filled) in enumerate([("Single year", False), ("Three-year averages", True)]):
        row = r[(r.group == g) & (r.spec == spec)].iloc[0]
        y = i * 1.0 + (0.17 if j == 0 else -0.17)
        ax.plot([row.ci_low, row.ci_high], [y, y], color=COLOR[g], linewidth=2,
                solid_capstyle="round")
        ax.plot(row.ige, y, "o", markersize=9, color=COLOR[g],
                markerfacecolor=COLOR[g] if filled else "white", markeredgewidth=2)
        ax.text(row.ci_high + 0.02, y, f"{row.ige:.2f}", va="center", fontsize=9.5, color=INK)
ax.set_yticks(range(len(groups)), [f"{LABEL[g]}\n(n = {int(r[r.group == g].n.iloc[0])})"
                                   for g in groups])
ax.invert_yaxis()
ax.axvline(0, color=MUTED, linewidth=0.8)
ax.set_xlabel("Intergenerational elasticity (IGE)")
ax.plot([], [], "o", color=INK, markerfacecolor="white", markeredgewidth=2,
        label="Single year (parents 1981, child 2012)")
ax.plot([], [], "o", color=INK, label="Three-year averages (1980–82, 2010–14)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, fontsize=9.5)
finish(ax, "Averaging raised the estimate for daughters, not for sons",
       "Weighted log–log slopes, 95% intervals clustered by mother. Same children in both rows.")
fig.savefig(RES / "ige-single-vs-average.png")
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 2. IGE by the child's age when earnings are measured (fixed group)
# ---------------------------------------------------------------------------
b = pd.read_csv(RES / "ige_by_year.csv")
fig, ax = plt.subplots(figsize=(8, 4.6))
for g in ["daughters", "sons", "all children"]:
    s = b[b.group == g].sort_values("mean_age")
    style = dict(color=COLOR[g], linewidth=2, marker="o", markersize=7,
                 linestyle="--" if g == "all children" else "-")
    for part in [s[s.income_year < 2008], s[s.income_year > 2008]]:   # no data 2005-2009
        ax.plot(part.mean_age, part.ige, **style)
        if g != "all children":
            ax.fill_between(part.mean_age, part.ci_low, part.ci_high, color=COLOR[g],
                            alpha=0.08, linewidth=0)
    last = s.iloc[-1]
    ax.text(last.mean_age + 0.4, last.ige, f"{LABEL[g]} (n = {int(last.n)})",
            va="center", fontsize=9.5, color=INK)
ax.axvspan(32.3, 36.8, color="#f3f4f1", zorder=0)
ax.text(34.55, 0.02, "not measured\n(2005–2009)", ha="center", fontsize=8.5, color=MUTED)
ax.set_xlim(26.5, 47)
ax.set_xticks(range(28, 44, 2))
ax.set_ylim(0, None)
ax.set_xlabel("Average age of the children in the earnings year")
ax.set_ylabel("IGE (parent income averaged 1980–82)")
ax.grid(axis="y", color=GRID, linewidth=0.8)
finish(ax, "Sons' measured IGE climbs as their earnings are observed later",
       "Same children every year: positive earnings in all six years. Shaded: 95% intervals.")
fig.savefig(RES / "ige-by-age.png")
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 3. One bad year: the $1 bottom code, sons
# ---------------------------------------------------------------------------
s = pd.read_csv(RES / "ige_bottomcode_sensitivity.csv")
s = s[s.group == "sons"]
fig, ax = plt.subplots(figsize=(8, 3.4))
for i, spec in enumerate(["Single year", "Three-year averages"]):
    bad = s[(s.spec == spec) & s.treatment.str.startswith("$1 code treated as income")].iloc[0]
    ok = s[(s.spec == spec) & s.treatment.str.contains("no income")].iloc[0]
    ax.annotate("", xy=(ok.ige, i), xytext=(bad.ige, i),
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=1.5))
    ax.plot(bad.ige, i, "o", markersize=9, color=COLOR["sons"], markerfacecolor="white",
            markeredgewidth=2)
    ax.plot(ok.ige, i, "o", markersize=9, color=COLOR["sons"])
    if abs(bad.ige - ok.ige) < 0.05:
        ax.text(ok.ige, i - 0.28, f"{bad.ige:.2f} vs {ok.ige:.2f}", ha="center", fontsize=9.5, color=INK)
    else:
        ax.text(bad.ige, i - 0.28, f"{bad.ige:.2f}", ha="center", fontsize=9.5, color=INK)
        ax.text(ok.ige, i - 0.28, f"{ok.ige:.2f}", ha="center", fontsize=9.5, color=INK)
ax.set_yticks([0, 1], ["Single year", "Three-year\naverages"])
ax.set_ylim(1.5, -0.6)
ax.set_xlim(0, 0.8)
ax.set_xlabel("IGE for sons")
ax.plot([], [], "o", color=COLOR["sons"], markerfacecolor="white", markeredgewidth=2,
        label="$1 code read as a real $1 income")
ax.plot([], [], "o", color=COLOR["sons"], label="$1 code read as no positive income")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=2, frameon=False, fontsize=9.5)
n_bad = int(s[s.treatment.str.startswith("$1 code treated as income")].n.iloc[0])
n_ok = int(s[s.treatment.str.contains("no income")].n.iloc[0])
extra = f"{n_bad - n_ok} son" + ("" if n_bad - n_ok == 1 else "s")
finish(ax, "One bad year moves the single-year estimate, not the average",
       f"Sons. Hollow: adds back {extra} whose 1981 family income is PSID's $1 bottom code "
       f"(n = {n_bad} vs {n_ok}).")
fig.savefig(RES / "one-bad-year.png")
plt.close(fig)
print("figures written")
