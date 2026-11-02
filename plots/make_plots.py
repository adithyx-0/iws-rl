"""Plots and results table for IWS-RL (M3, T3.3).  Only reads result files; never edits them.

Usage (defaults = current v2 results):
    python plots/make_plots.py
    python plots/make_plots.py --results-dir results_final --out-dir plots/final --baseline ce_schedule
Optional inputs (skipped with a message if the file is absent):
    --oracle      CSV with columns scenario, mean_sr, min_zone_sr           (default: <results-dir>/oracle.csv)
    --pareto      CSV with columns label, mean_sr, min_zone_sr [,mean_sr_lo, mean_sr_hi, min_zone_sr_lo, min_zone_sr_hi]
                  (e.g. M2's lambda / Lagrangian sweep, once it exists)
    --curves      glob of learning-curve CSVs with columns step, mean_sr (one file per seed)
"""
import argparse, glob, os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

p = argparse.ArgumentParser()
p.add_argument("--results-dir", default="results_v2", help="folder with summary.csv and episodes.csv")
p.add_argument("--summary", default=None, help="override path to summary.csv")
p.add_argument("--episodes", default=None, help="override path to episodes.csv")
p.add_argument("--oracle", default=None)
p.add_argument("--pareto", default=None)
p.add_argument("--curves", default=None)
p.add_argument("--out-dir", default="plots/out")
p.add_argument("--condition", default="default", help="condition used for the bar chart, scatter and table")
p.add_argument("--baseline", default="ce_schedule", help="method family that differences are measured against")
p.add_argument("--exclude-methods", default="", help="comma-separated families to hide")
p.add_argument("--include-scarce", action="store_true", help="keep the degenerate 'scarce' condition in the heatmap")
p.add_argument("--lambda-sweep", action="store_true", help="draw the PPO lambda sweep from summary.csv (families ppo_lam*)")
a = p.parse_args()

summary_path = a.summary or os.path.join(a.results_dir, "summary.csv")
episodes_path = a.episodes or os.path.join(a.results_dir, "episodes.csv")
oracle_path = a.oracle or os.path.join(a.results_dir, "oracle.csv")
os.makedirs(a.out_dir, exist_ok=True)

if not os.path.exists(summary_path):
    sys.exit(f"missing {summary_path} (use --results-dir or --summary)")
S = pd.read_csv(summary_path)
hide = {x for x in a.exclude_methods.split(",") if x}
S = S[~S.family.isin(hide)]
if a.condition not in set(S.condition):
    sys.exit(f"condition '{a.condition}' not in {summary_path}; available: {sorted(set(S.condition))}")

LABEL = {"ppo": "PPO", "ce_schedule": "Old CE schedule (under-tuned)", "ce_tuned": "Tuned fixed schedule",
         "ppo_lam0": "PPO λ=0", "ppo_lam0.5": "PPO λ=0.5", "ppo_lam2": "PPO λ=2", "ppo_lam4": "PPO λ=4", "greedy_k1": "Greedy k1", "greedy_k2": "Greedy k2",
         "priv_greedy_k1": "Privileged greedy", "random": "Random", "all_open": "All open", "rota_k1": "Rota k1",
         "dqn": "DQN", "ppo_noequity": "PPO no-equity", "ppo_noforecast": "PPO no-forecast",
         "rec": "LSTM PPO", "rec_dr": "LSTM PPO + DR", "ppo_dr": "PPO + DR", "a2c": "A2C", "ppo_long": "PPO 500k"}
lab = lambda f: LABEL.get(f, f)
PRIV = {"priv_greedy_k1"}                       # uses hidden info: draw hatched / flag in table
saved = []


def save(fig, name):
    path = os.path.join(a.out_dir, name); fig.savefig(path, dpi=160, bbox_inches="tight"); plt.close(fig); saved.append(path)


D = S[S.condition == a.condition].sort_values("mean_sr", ascending=False)

# 1. bar chart with 95% CI: mean supply and worst-zone supply
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)
for ax, k, title in zip(axs, ["mean_sr", "min_zone_sr"], ["Mean supply ratio", "Worst-zone supply ratio"]):
    d = D.sort_values(k, ascending=True)
    err = np.vstack([d[k] - d[k + "_lo"], d[k + "_hi"] - d[k]])
    bars = ax.barh([lab(f) for f in d.family], d[k], xerr=err, color="#4C78A8", capsize=2)
    for b, f in zip(bars, d.family):
        if f in PRIV: b.set_hatch("//"); b.set_alpha(0.6)
        if f == a.baseline: b.set_color("#F58518")
    ax.set_title(f"{title} ({a.condition})"); ax.set_xlim(max(0, d[k].min() - 0.08), min(1, d[k].max() + 0.05))
    ax.grid(axis="x", alpha=.3)
fig.suptitle("Higher is better. Error bars: 95% bootstrap CI over scenarios. Hatched = uses hidden tank levels (not deployable). Orange = baseline.", fontsize=8)
save(fig, "bars_ci.png")

# 2. mean vs worst-zone scatter (+ oracle if available)
fig, ax = plt.subplots(figsize=(6.2, 5))
for _, r in D.iterrows():
    ax.errorbar(r.mean_sr, r.min_zone_sr, xerr=[[r.mean_sr - r.mean_sr_lo], [r.mean_sr_hi - r.mean_sr]],
                yerr=[[r.min_zone_sr - r.min_zone_sr_lo], [r.min_zone_sr_hi - r.min_zone_sr]], fmt="o" if r.family not in PRIV else "s",
                capsize=2, label=lab(r.family))
    ax.annotate(lab(r.family), (r.mean_sr, r.min_zone_sr), textcoords="offset points", xytext=(4, 4), fontsize=7)
if os.path.exists(oracle_path):
    o = pd.read_csv(oracle_path)
    ax.scatter([o.mean_sr.mean()], [o.min_zone_sr.mean()], marker="*", s=160, c="k", zorder=5)
    ax.annotate("Oracle (30 scen., uses future info)", (o.mean_sr.mean(), o.min_zone_sr.mean()), textcoords="offset points", xytext=(4, -10), fontsize=7)
else:
    print(f"[skip] oracle point: {oracle_path} not found")
ax.set_xlabel("Mean supply ratio"); ax.set_ylabel("Worst-zone supply ratio"); ax.set_title(f"Efficiency vs equity ({a.condition})"); ax.grid(alpha=.3)
save(fig, "scatter_mean_vs_worst.png")

# 2b. lambda sweep straight from summary.csv (families ppo_lam0, ppo_lam0.5, ppo (=lambda 1), ppo_lam2, ppo_lam4)
if a.lambda_sweep:
    LAM = [("ppo_lam0", 0.0), ("ppo_lam0.5", 0.5), ("ppo", 1.0), ("ppo_lam2", 2.0), ("ppo_lam4", 4.0)]
    L = D.set_index("family"); pts = [(lm, L.loc[f]) for f, lm in LAM if f in L.index]
    if len(pts) >= 3:
        fig, ax = plt.subplots(figsize=(6.4, 5))
        xs = [r.mean_sr for _, r in pts]; ys = [r.min_zone_sr for _, r in pts]
        ax.plot(xs, ys, "-", color="#999", zorder=1)
        for lm, r in pts:
            ax.errorbar(r.mean_sr, r.min_zone_sr, xerr=[[r.mean_sr - r.mean_sr_lo], [r.mean_sr_hi - r.mean_sr]],
                        yerr=[[r.min_zone_sr - r.min_zone_sr_lo], [r.min_zone_sr_hi - r.min_zone_sr]], fmt="o", color="#4C78A8", capsize=2, zorder=2)
            ax.annotate(f"λ={lm:g} ({int(r.n_seeds)} seeds)", (r.mean_sr, r.min_zone_sr), textcoords="offset points", xytext=(5, -11), fontsize=7)
        for f, nm, c in [(a.baseline, lab(a.baseline), "#F58518"), ("dqn", "DQN", "#54A24B"), ("ppo_dr", "PPO + DR", "#B279A2")]:
            if f in L.index:
                r = L.loc[f]; ax.errorbar(r.mean_sr, r.min_zone_sr, xerr=[[r.mean_sr - r.mean_sr_lo], [r.mean_sr_hi - r.mean_sr]],
                                          yerr=[[r.min_zone_sr - r.min_zone_sr_lo], [r.min_zone_sr_hi - r.min_zone_sr]], fmt="s", color=c, capsize=2)
                ax.annotate(nm, (r.mean_sr, r.min_zone_sr), textcoords="offset points", xytext=(5, 4), fontsize=7)
        ax.set_xlabel("Mean supply ratio"); ax.set_ylabel("Worst-zone supply ratio")
        ax.set_title(f"Equity weight λ in the PPO reward ({a.condition}); a reward penalty, not a constraint", fontsize=8); ax.grid(alpha=.3)
        save(fig, "pareto_lambda.png")
    else:
        print("[skip] lambda sweep: fewer than 3 lambda families in summary")

# 3. pareto from an external sweep (M2), if given
if a.pareto:
    if os.path.exists(a.pareto):
        P = pd.read_csv(a.pareto); need = {"label", "mean_sr", "min_zone_sr"}
        if need <= set(P.columns):
            fig, ax = plt.subplots(figsize=(6.2, 5))
            for _, r in P.iterrows():
                xe = [[r.mean_sr - r.mean_sr_lo], [r.mean_sr_hi - r.mean_sr]] if "mean_sr_lo" in P else None
                ye = [[r.min_zone_sr - r.min_zone_sr_lo], [r.min_zone_sr_hi - r.min_zone_sr]] if "min_zone_sr_lo" in P else None
                ax.errorbar(r.mean_sr, r.min_zone_sr, xerr=xe, yerr=ye, fmt="o", capsize=2); ax.annotate(str(r.label), (r.mean_sr, r.min_zone_sr), textcoords="offset points", xytext=(4, 4), fontsize=7)
            ax.set_xlabel("Mean supply ratio"); ax.set_ylabel("Worst-zone supply ratio"); ax.set_title("Equity trade-off sweep"); ax.grid(alpha=.3)
            save(fig, "pareto.png")
        else:
            print(f"[skip] pareto: {a.pareto} needs columns {sorted(need)}")
    else:
        print(f"[skip] pareto: {a.pareto} not found")

# 4. regime heatmap: paired difference vs baseline per condition (from episodes.csv, per-scenario pairing)
if os.path.exists(episodes_path):
    E = pd.read_csv(episodes_path)
    E["family"] = E.family if "family" in E else E.method.str.replace(r"_s\d+$", "", regex=True)
    E = E[~E.family.isin(hide)]
    if not a.include_scarce: E = E[E.condition != "scarce"]
    if a.baseline not in set(E.family):
        print(f"[skip] heatmap: baseline '{a.baseline}' not in episodes")
    else:
        per = E.groupby(["condition", "family", "scenario"])[["mean_sr", "min_zone_sr"]].mean().reset_index()
        for k, fn in [("mean_sr", "heatmap_mean_vs_baseline.png"), ("min_zone_sr", "heatmap_worst_vs_baseline.png")]:
            base = per[per.family == a.baseline].set_index(["condition", "scenario"])[k]
            per["d"] = per.apply(lambda r: r[k] - base.get((r.condition, r.scenario), np.nan), axis=1)
            M = per[per.family != a.baseline].groupby(["family", "condition"]).d.mean().unstack()
            M = M.loc[M.mean(axis=1).sort_values(ascending=False).index]
            fig, ax = plt.subplots(figsize=(1.0 + 0.95 * M.shape[1], 0.9 + 0.45 * M.shape[0]))
            v = np.nanmax(np.abs(M.values)); im = ax.imshow(M.values, cmap="RdBu", vmin=-v, vmax=v, aspect="auto")
            ax.set_xticks(range(M.shape[1])); ax.set_xticklabels(M.columns, rotation=45, ha="right", fontsize=8)
            ax.set_yticks(range(M.shape[0])); ax.set_yticklabels([lab(f) for f in M.index], fontsize=8)
            for i in range(M.shape[0]):
                for j in range(M.shape[1]): ax.text(j, i, f"{M.values[i, j]:+.3f}", ha="center", va="center", fontsize=6.5)
            ax.set_title(f"{k}: method minus {lab(a.baseline)} (paired means; blue = better than baseline)", fontsize=8)
            fig.colorbar(im, ax=ax, shrink=0.8); save(fig, fn)
else:
    print(f"[skip] heatmaps: {episodes_path} not found")

# 5. learning curves, if provided
tuned_ref = {}
try:
    _r = S[(S.family == a.baseline) & (S.condition == 'default')].iloc[0]
    tuned_ref = {'mean_sr': float(_r['mean_sr']), 'min_zone_sr': float(_r['min_zone_sr'])}
except Exception as e: print('[note] no tuned reference line:', e)
if a.curves:
    files = sorted(glob.glob(a.curves))
    if files:
        cs = []
        for f in files:
            c = pd.read_csv(f)
            if {"step", "mean_sr"} <= set(c.columns): cs.append((os.path.basename(f), c))
            else: print(f"[skip] curve {f}: needs columns step, mean_sr")
        if cs:
            has_w = all("min_zone_sr" in c.columns for _, c in cs)
            fig, axs = plt.subplots(1, 2 if has_w else 1, figsize=(10, 4.2), squeeze=False); axs = axs[0]
            cols = ["mean_sr", "min_zone_sr"][:len(axs)]; labs = ["Mean supply ratio", "Worst-zone supply ratio"]
            for ax, col, ylab in zip(axs, cols, labs):
                for i, (n, c) in enumerate(cs): ax.plot(c.step, c[col], alpha=.8, label=f"PPO seed {i}")
                ref = tuned_ref.get(col)
                if ref is not None: ax.axhline(ref, color="#B85A0B", ls="--", lw=1.5, label=f"{a.baseline} (default test)")
                ax.set_xlabel("Training steps"); ax.set_ylabel(ylab + " (test seeds 10000-10009)"); ax.grid(alpha=.3); ax.legend(fontsize=8)
            fig.tight_layout(); save(fig, "learning_curves.png")
    else:
        print(f"[skip] curves: no files match {a.curves}")

# 6. results table (markdown + csv) for the chosen condition
cols = ["family", "n_seeds", "mean_sr", "mean_sr_lo", "mean_sr_hi", "min_zone_sr", "min_zone_sr_lo", "min_zone_sr_hi", "jain_zone" if "jain_zone" in D else "gini_node"]
T = D[[c for c in cols if c in D]].copy(); T.insert(1, "uses_hidden_info", T.family.isin(PRIV))
T.to_csv(os.path.join(a.out_dir, "results_table.csv"), index=False)
md = ["| Method | seeds | mean supply [95% CI] | worst zone [95% CI] | hidden info |", "|---|---|---|---|---|"]
for _, r in T.iterrows():
    md.append(f"| {lab(r.family)} | {int(r.n_seeds)} | {r.mean_sr:.3f} [{r.mean_sr_lo:.3f}, {r.mean_sr_hi:.3f}] | "
              f"{r.min_zone_sr:.3f} [{r.min_zone_sr_lo:.3f}, {r.min_zone_sr_hi:.3f}] | {'yes' if r.uses_hidden_info else ''} |")
open(os.path.join(a.out_dir, "results_table.md"), "w", encoding="utf-8").write(f"Condition: {a.condition}. Source: {summary_path}\n\n" + "\n".join(md) + "\n")
saved += [os.path.join(a.out_dir, "results_table.csv"), os.path.join(a.out_dir, "results_table.md")]
print("wrote:\n  " + "\n  ".join(saved))
