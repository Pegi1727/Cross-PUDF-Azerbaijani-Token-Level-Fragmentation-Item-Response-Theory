#!/usr/bin/env python3
"""Generate publication-ready Figures 1–5 for the cross-PUDf study.

Reads cross_pudf_100_sentences_scores.csv and cross_pudf_sampling_batches.csv
from the script directory by default (or paths passed on the command line).
Writes 300-dpi PNG and vector PDF files to ./cross_pudf_figures.

Dependencies: numpy, pandas, matplotlib. Usage:
  python generate_cross_pudf_figures.py [scores.csv] [sampling_batches.csv] [output_dir]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.ticker import MaxNLocator

HERE = Path(__file__).resolve().parent
SCORES_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "cross_pudf_100_sentences_scores.csv"
SAMPLE_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "cross_pudf_sampling_batches.csv"
OUTDIR = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "cross_pudf_figures"
OUTDIR.mkdir(parents=True, exist_ok=True)

# Colorblind-friendly academic palette; tier order is fixed throughout.
TIERS = ["basic_everyday", "intermediate_narrative", "advanced_academic_technical", "morphologically_complex"]
TIER_LABELS = ["Basic everyday", "Intermediate narrative", "Advanced academic/technical", "Morphologically complex"]
COLORS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7"]
NAVY, INK, MUTED, GRID = "#17324D", "#243746", "#596B78", "#DCE4EA"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 11,
    "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "figure.titlesize": 15, "figure.titleweight": "bold",
    "axes.titleweight": "bold", "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "axes.linewidth": 0.8,
    "savefig.facecolor": "white", "figure.facecolor": "white",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})


def load_data():
    if not SCORES_PATH.exists():
        raise FileNotFoundError(f"Scores CSV not found: {SCORES_PATH}")
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError(f"Sampling CSV not found: {SAMPLE_PATH}")
    score, samp = pd.read_csv(SCORES_PATH), pd.read_csv(SAMPLE_PATH)
    required_s = {"row_id", "tier", "sentence", "unicode_word_count", "source_token_count", "target_token_count", "target_token_to_word_fertility", "target_source_token_ratio", "target_surface_nonoverlap_proxy", "b_tilde", "b_tilde_zscore"}
    required_p = {"theta", "batch_number", "row_id", "tier", "fisher_information_weight", "probability_correct_at_theta", "selection_probability"}
    if missing := required_s - set(score.columns):
        raise ValueError(f"Scores CSV missing columns: {sorted(missing)}")
    if missing := required_p - set(samp.columns):
        raise ValueError(f"Sampling CSV missing columns: {sorted(missing)}")
    if score.row_id.duplicated().any() or len(score) != 100:
        raise ValueError("Expected 100 score rows with unique row_id values")
    if set(score.tier) != set(TIERS):
        raise ValueError("Unexpected/missing tier labels in scores file")
    if score.groupby("tier").size().to_dict() != {t: 25 for t in TIERS}:
        raise ValueError("Expected exactly 25 sentences per tier")
    return score, samp


def style_ax(ax, grid_axis="y"):
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, color=GRID, linewidth=.7, alpha=.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)


def save(fig, n):
    fig.savefig(OUTDIR / f"cross_pudf_figure_{n}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTDIR / f"cross_pudf_figure_{n}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Figure {n}: {OUTDIR / f'cross_pudf_figure_{n}.png'} and PDF")


def figure1():
    """Study workflow and operationalization diagram."""
    fig, ax = plt.subplots(figsize=(11.2, 5.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    fig.suptitle("Cross-PUDF study: data-to-selection workflow", color=NAVY, y=.96)
    boxes = [
        (.035, .58, .205, .25, "01  SENTENCE SET", "100 Azerbaijani sentences\n4 tiers × 25 items", "#EAF2F8"),
        (.285, .58, .205, .25, "02  TOKENIZATION", "bert-base-uncased\nbert-base-multilingual-cased", "#E8F4F1"),
        (.535, .58, .205, .25, "03  ITEM MEASURES", "Word count · token counts\nFertility · overlap proxy", "#FFF4E5"),
        (.785, .58, .18, .25, "04  SCORE", "b̃ = fertility\n+ non-overlap proxy", "#F6ECF3"),
    ]
    for x, y, w, h, head, body, fc in boxes:
        patch = FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.012,rounding_size=0.018",facecolor=fc,edgecolor="#C7D4DE",linewidth=1.1)
        ax.add_patch(patch)
        ax.text(x+.014,y+h-.055,head,fontsize=9,fontweight="bold",color=NAVY,va="top")
        ax.text(x+.014,y+.085,body,fontsize=9,color=INK,va="center",linespacing=1.45)
    for x1,x2 in [(.24,.285),(.49,.535),(.74,.785)]:
        ax.add_patch(FancyArrowPatch((x1+.005,.705),(x2-.007,.705),arrowstyle="-|>",mutation_scale=13,color="#718797",linewidth=1.4))
    # Lower branch summarizes scaling and illustrative item selection.
    lower = [(.13,.16,.31,.22,"SCORE TRANSFORMS","z-score · min–max [−3, 3]\nrobust p5–p95 scaling"),(.56,.16,.31,.22,"ILLUSTRATIVE ZPD SAMPLING","2PL: a = clipped fertility, b = z-score\nFisher information weighting at θ = −2, 0, +2")]
    for x,y,w,h,head,body in lower:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.012,rounding_size=0.018",facecolor="#F4F7F9",edgecolor="#C7D4DE",linewidth=1.05))
        ax.text(x+.018,y+h-.055,head,fontsize=9,fontweight="bold",color=NAVY,va="top")
        ax.text(x+.018,y+.075,body,fontsize=8.6,color=INK,va="center",linespacing=1.4)
    ax.add_patch(FancyArrowPatch((.875,.57),(.73,.40),connectionstyle="arc3,rad=-.12",arrowstyle="-|>",mutation_scale=13,color="#718797",linewidth=1.3))
    ax.add_patch(FancyArrowPatch((.44,.27),(.56,.27),arrowstyle="-|>",mutation_scale=13,color="#718797",linewidth=1.3))
    ax.text(.5,.055,"Interpretation note: surface non-overlap is a vocabulary-string proxy, not semantic or lexical coverage.",ha="center",fontsize=8.4,color=MUTED)
    save(fig,1)


def figure2(score):
    """Tier-wise distributions for token fertility and source/target ratio."""
    fig, axes = plt.subplots(1,2,figsize=(11.5,4.8), gridspec_kw={"wspace":.3})
    fig.suptitle("Sentence-level tokenization burden by proficiency tier",color=NAVY,y=.99)
    metrics=[("target_token_to_word_fertility","Target tokens per word","Target token fertility"),("target_source_token_ratio","target / source token count","Target-to-source token ratio")]
    rng=np.random.default_rng(19)
    for ax,(col,sub,title) in zip(axes,metrics):
        vals=[score.loc[score.tier.eq(t),col].dropna().values for t in TIERS]
        bp=ax.boxplot(vals,positions=np.arange(4),widths=.52,patch_artist=True,showfliers=False,medianprops={"color":NAVY,"linewidth":1.7},whiskerprops={"color":"#7A8D9B"},capprops={"color":"#7A8D9B"})
        for i,(patch,v,c) in enumerate(zip(bp["boxes"],vals,COLORS)):
            patch.set_facecolor(c); patch.set_alpha(.22); patch.set_edgecolor(c); patch.set_linewidth(1.3)
            x=rng.normal(i,.055,len(v)); ax.scatter(x,v,s=16,color=c,alpha=.68,edgecolors="white",linewidths=.25,zorder=3)
        ax.set_xticks(range(4),TIER_LABELS,rotation=18,ha="right")
        ax.set_ylabel(title); ax.set_title(sub,pad=10,color=NAVY); style_ax(ax)
        ax.set_xlim(-.55,3.55)
    fig.subplots_adjust(bottom=.24,top=.84,left=.08,right=.98)
    save(fig,2)


def figure3(score):
    """Score distributions and component means by tier."""
    fig,axes=plt.subplots(1,2,figsize=(11.6,4.8),gridspec_kw={"width_ratios":[1.05,1],"wspace":.34})
    fig.suptitle("Composite score and its measured components",color=NAVY,y=.99)
    ax=axes[0]; rng=np.random.default_rng(7)
    vals=[score.loc[score.tier.eq(t),"b_tilde"].values for t in TIERS]
    bp=ax.boxplot(vals,positions=np.arange(4),widths=.54,patch_artist=True,showfliers=False,medianprops={"color":NAVY,"linewidth":1.7},whiskerprops={"color":"#7A8D9B"},capprops={"color":"#7A8D9B"})
    for i,(p,v,c) in enumerate(zip(bp["boxes"],vals,COLORS)):
        p.set_facecolor(c);p.set_alpha(.22);p.set_edgecolor(c);p.set_linewidth(1.25)
        ax.scatter(rng.normal(i,.055,len(v)),v,s=14,color=c,alpha=.6,edgecolors="white",linewidths=.2,zorder=3)
    ax.set_xticks(range(4),["Basic","Intermediate","Advanced","Morphological"],rotation=20,ha="right")
    ax.set_ylabel("b̃ (fertility + non-overlap proxy)");ax.set_title("Composite score by tier",color=NAVY);style_ax(ax)
    ax=axes[1]
    cols=["target_token_to_word_fertility","target_surface_nonoverlap_proxy"]
    means=score.groupby("tier").mean(numeric_only=True).reindex(TIERS)
    # Components deliberately remain on their native scales; annotate distinct axes.
    x=np.arange(4); width=.34
    bars1=ax.bar(x-width/2,means[cols[0]],width,color=COLORS[0],label="Fertility",alpha=.9)
    ax.set_ylabel("Mean target tokens / word",color=COLORS[0]);ax.tick_params(axis="y",labelcolor=COLORS[0])
    ax2=ax.twinx();bars2=ax2.bar(x+width/2,means[cols[1]],width,color="#D55E00",label="Non-overlap proxy",alpha=.83)
    ax2.set_ylabel("Mean surface non-overlap proxy",color="#B04B00");ax2.tick_params(axis="y",labelcolor="#B04B00");ax2.set_ylim(0,1)
    ax.set_xticks(x,["Basic","Intermediate","Advanced","Morphological"],rotation=20,ha="right")
    ax.set_title("Mean score components (native scales)",color=NAVY);style_ax(ax)
    ax2.spines["top"].set_visible(False);ax2.spines["right"].set_color(GRID);ax2.grid(False)
    ax.legend([bars1,bars2],["Fertility","Non-overlap proxy"],frameon=False,loc="upper left",fontsize=8)
    fig.subplots_adjust(bottom=.22,top=.84,left=.08,right=.91)
    save(fig,3)


def figure4(score):
    """Faceted sentence-length/token-count relationship; small multiples prevent label crowding."""
    fig,axes=plt.subplots(2,2,figsize=(10.4,7.2),sharex=True,sharey=True)
    fig.suptitle("Sentence length and target-token count",color=NAVY,y=.985)
    rng=np.random.default_rng(2024)
    for i,(ax,t,label,c) in enumerate(zip(axes.flat,TIERS,TIER_LABELS,COLORS)):
        part=score.loc[score.tier.eq(t)]
        x=part.unicode_word_count.to_numpy(dtype=float);y=part.target_token_count.to_numpy(dtype=float)
        # Minimal jitter separates repeated integer observations without distorting trend.
        xj=x+rng.uniform(-.075,.075,len(x)); yj=y+rng.uniform(-.12,.12,len(y))
        ax.scatter(xj,yj,s=38,color=c,alpha=.76,edgecolors="white",linewidths=.65,zorder=3)
        coef=np.polyfit(x,y,1); xx=np.linspace(x.min()-.4,x.max()+.4,100); ax.plot(xx,np.polyval(coef,xx),color=c,lw=1.7,alpha=.9)
        r=float(np.corrcoef(x,y)[0,1]) if np.std(x)>0 and np.std(y)>0 else float("nan")
        ax.set_title(f"{label}  ·  n={len(part)}  ·  r={r:.2f}",color=NAVY,pad=8,fontsize=9)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True,nbins=6));ax.yaxis.set_major_locator(MaxNLocator(integer=True,nbins=6))
        style_ax(ax)
        ax.margins(x=.08,y=.12)
    axes[1,0].set_xlabel("Unicode word count");axes[1,1].set_xlabel("Unicode word count")
    axes[0,0].set_ylabel("Target tokenizer tokens");axes[1,0].set_ylabel("Target tokenizer tokens")
    # Compact explanatory caption, clear of axes and labels.
    fig.text(.5,.018,"Points are individual sentences; lines show within-tier least-squares fits. Jitter is visual only.",ha="center",fontsize=8.3,color=MUTED)
    fig.subplots_adjust(left=.09,right=.985,bottom=.10,top=.88,hspace=.31,wspace=.18)
    save(fig,4)


def figure5(samp):
    """Sampling composition and selected-item information across theta."""
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.8),gridspec_kw={"width_ratios":[1.12,1],"wspace":.34})
    fig.suptitle("Illustrative Fisher-information-weighted ZPD sampling",color=NAVY,y=.99)
    thetas=sorted(samp.theta.unique()); xpos=np.arange(len(thetas))
    ax=axes[0]; bottom=np.zeros(len(thetas))
    for t,label,c in zip(TIERS,TIER_LABELS,COLORS):
        counts=np.array([int(((samp.theta==th)&(samp.tier==t)).sum()) for th in thetas])
        ax.bar(xpos,counts,bottom=bottom,color=c,width=.62,label=label,edgecolor="white",linewidth=.6)
        for j,(b,n) in enumerate(zip(bottom,counts)):
            if n>=4: ax.text(j,b+n/2,str(n),ha="center",va="center",fontsize=8,color="white" if c in (COLORS[0],COLORS[2]) else INK,fontweight="bold")
        bottom += counts
    ax.set_xticks(xpos,[f"{th:g}" for th in thetas]);ax.set_xlabel("Ability level (θ)");ax.set_ylabel("Selected items (pooled over batches)")
    ax.set_title("Tier composition · 50 selections per θ",color=NAVY);ax.set_ylim(0,max(bottom)*1.16);style_ax(ax)
    ax.legend(frameon=False,fontsize=7.3,loc="upper left",bbox_to_anchor=(0,1.01),ncol=1)
    ax=axes[1]
    grouped=samp.groupby("theta")
    mean_info=grouped.fisher_information_weight.mean().reindex(thetas).to_numpy()
    mean_prob=grouped.probability_correct_at_theta.mean().reindex(thetas).to_numpy()
    sd_info=grouped.fisher_information_weight.std().reindex(thetas).fillna(0).to_numpy()
    ax.errorbar(xpos-.08,mean_info,yerr=sd_info,fmt="o-",color="#0072B2",lw=1.8,ms=6,capsize=3,label="Fisher information (mean ± SD)")
    ax.set_ylabel("Selected-item Fisher information",color="#0072B2");ax.tick_params(axis="y",labelcolor="#0072B2")
    ax2=ax.twinx();ax2.plot(xpos+.08,mean_prob,"s--",color="#D55E00",lw=1.7,ms=5,label="Mean P(correct)")
    ax2.set_ylabel("Mean probability correct",color="#B04B00");ax2.tick_params(axis="y",labelcolor="#B04B00");ax2.set_ylim(0,1)
    ax.set_xticks(xpos,[f"{th:g}" for th in thetas]);ax.set_xlabel("Ability level (θ)");ax.set_title("Selected-item characteristics",color=NAVY);style_ax(ax);ax2.grid(False);ax2.spines["top"].set_visible(False)
    h1,l1=ax.get_legend_handles_labels();h2,l2=ax2.get_legend_handles_labels();ax.legend(h1+h2,l1+l2,frameon=False,fontsize=7.5,loc="upper center")
    fig.text(.5,.025,"Sampling is illustrative, without replacement within each θ; it is not a validated assessment calibration.",ha="center",fontsize=8.2,color=MUTED)
    fig.subplots_adjust(bottom=.17,top=.83,left=.09,right=.91)
    save(fig,5)


def main():
    score,samp=load_data()
    figure1();figure2(score);figure3(score);figure4(score);figure5(samp)
    outputs=sorted(p.name for p in OUTDIR.glob("cross_pudf_figure_*"))
    if len(outputs)!=10: raise RuntimeError(f"Expected 10 output files, found {len(outputs)}: {outputs}")
    print(f"SUCCESS: generated {len(outputs)} figure files in {OUTDIR}")

if __name__ == "__main__":
    main()
