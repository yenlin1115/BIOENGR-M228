#!/usr/bin/env python3
"""Generate pipeline_comparison.png matching the current two-stage GBM model."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(14, 9.2))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9.2)
ax.axis("off")
fig.patch.set_facecolor("#F5F5F5")
ax.set_facecolor("#F5F5F5")

C_DARK   = "#2C3E50"
C_LIGHT  = "#ECF0F1"
C_SHARED = "#27AE60"
C_ROUTE  = "#8E44AD"
C_CCU    = "#16A085"
C_CSRU   = "#E67E22"
C_MICU   = "#6C3483"
C_SICU   = "#C0392B"
C_PRED   = "#7F8C8D"
C_DIV    = "#BDC3C7"


def box(ax, cx, cy, w, h, label, facecolor, textcolor="white", fontsize=9.5,
        bold=True, radius=0.15):
    rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                          boxstyle=f"round,pad=0.05,rounding_size={radius}",
                          facecolor=facecolor, edgecolor=facecolor,
                          linewidth=1.8, zorder=3)
    ax.add_patch(rect)
    ax.text(cx, cy, label, ha="center", va="center", fontsize=fontsize,
            color=textcolor, fontweight="bold" if bold else "normal",
            zorder=4, multialignment="center", linespacing=1.4)


def arrow(ax, x1, y1, x2, y2, color="#888888"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6,
                                mutation_scale=14), zorder=2)


# ── Title ────────────────────────────────────────────────────────────────────
ax.text(7, 8.85, "COMPARISON OF DATA PROCESSING PIPELINES",
        ha="center", va="center", fontsize=14, fontweight="bold", color=C_DARK)

# ── Divider ──────────────────────────────────────────────────────────────────
ax.plot([7, 7], [0.5, 8.55], color=C_DIV, lw=2, zorder=1)
ax.text(7, 4.60, "VS.", ha="center", va="center", fontsize=15,
        fontweight="bold", color=C_DIV,
        bbox=dict(fc="#F5F5F5", ec="none", pad=3))

# ════════════════════════════════════════════════════════════════════════════
# LEFT — Citi & Barbieri
# ════════════════════════════════════════════════════════════════════════════
LX = 3.3

ax.text(LX, 8.40, "Citi & Barbieri's Model", ha="center", fontsize=11.5,
        fontweight="bold", color=C_DARK)
ax.text(LX, 8.10, "(Original)", ha="center", fontsize=9, color="#777777")

box(ax, LX, 7.68, 3.2, 0.42, "PhysioNet 2012 Dataset",
    C_LIGHT, textcolor=C_DARK)
arrow(ax, LX, 7.47, LX, 7.02)

box(ax, LX, 6.78, 3.2, 0.48,
    "Feature Extraction\n& Normalization",
    C_LIGHT, textcolor=C_DARK, fontsize=9)
arrow(ax, LX, 6.54, LX, 6.08)

box(ax, LX, 5.84, 3.2, 0.48,
    "Global SVM Classifiers\n(6 SVMs, poly kernel)",
    C_DARK)
arrow(ax, LX, 5.60, LX, 5.14)

box(ax, LX, 4.90, 3.2, 0.42,
    "Probit GLM Combiner",
    C_LIGHT, textcolor=C_DARK)
arrow(ax, LX, 4.69, LX, 4.22)

box(ax, LX, 3.98, 3.2, 0.42,
    "Mortality Prediction", C_PRED)

# ════════════════════════════════════════════════════════════════════════════
# RIGHT — Our two-stage GBM + routing GLM
# ════════════════════════════════════════════════════════════════════════════
RX = 10.7
RW = 3.6   # box width

ax.text(RX, 8.40, "Our Department-Specific Approach", ha="center",
        fontsize=11.5, fontweight="bold", color=C_DARK)

box(ax, RX, 7.68, RW, 0.42, "PhysioNet 2012 Dataset",
    C_LIGHT, textcolor=C_DARK)
arrow(ax, RX, 7.47, RX, 7.02)

box(ax, RX, 6.78, RW, 0.48,
    "Feature Extraction & Normalization\n(187-dim, 48-hr summaries)",
    C_LIGHT, textcolor=C_DARK, fontsize=9)
arrow(ax, RX, 6.54, RX, 6.08)

# Shared GBM backbone
box(ax, RX, 5.84, RW, 0.56,
    "Shared GBM Backbone\n(HistGradientBoosting, all patients,\nno ICU type input)",
    C_SHARED, fontsize=8.8)
arrow(ax, RX, 5.56, RX, 5.18)

# ── ICU one-hot row ──────────────────────────────────────────────────────────
ax.text(RX, 5.12, "ICU type one-hot indicators (input to GLM):",
        ha="center", va="center", fontsize=7.8, color="#555555", style="italic")

icu_xs     = [8.88, 9.88, 10.88, 11.88]
icu_labels = ["CCU", "CSRU", "MICU", "SICU"]
icu_colors = [C_CCU, C_CSRU, C_MICU, C_SICU]
icu_y = 4.78

for icx, icl, icc in zip(icu_xs, icu_labels, icu_colors):
    box(ax, icx, icu_y, 0.82, 0.30, icl, icc, fontsize=8.5)
    arrow(ax, icx, icu_y - 0.15, icx, 4.38, color=icc)

# Routing GLM
box(ax, RX, 4.18, RW, 0.46,
    "Department Routing GLM\n(logit(GBM prob) + ICU one-hot → LR)",
    C_ROUTE, fontsize=8.8)
arrow(ax, RX, 3.95, RX, 3.48)

# Final prediction
box(ax, RX, 3.26, RW, 0.42,
    "Department-Adjusted Mortality Prediction",
    C_PRED)

# note
ax.text(RX, 2.75,
        "Backbone: pooled across all ICUs  |  GLM: adds per-department offsets",
        ha="center", fontsize=7.8, color="#888888", style="italic")

plt.tight_layout(pad=0.3)
plt.savefig("pipeline_comparison.png", dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved pipeline_comparison.png")
