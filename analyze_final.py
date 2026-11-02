"""Paired bootstrap CIs (over test scenarios) of family-mean differences vs ce_tuned; Pareto + regime-map figures.
Outputs results_v2/paired_vs_ce_tuned.csv, results_v2/figs/*.png. CIs exclude training-seed variance."""
import numpy as np, pandas as pd, os
e = pd.read_csv("results_v2/episodes.csv"); os.makedirs("results_v2/figs", exist_ok=True)
rng = np.random.default_rng(0)
def fam_mean(f, m):  # scenario-indexed mean over seeds of family f
    return e[e.family == f].groupby(["condition", "scenario"])[m].mean()
rows = []
for f in ["ppo", "ppo_dr", "dqn", "ppo_noequity", "ce_schedule"]:
    for m in ["return", "min_zone_sr", "mean_sr"]:
        d = (fam_mean(f, m) - fam_mean("ce_tuned", m)).dropna()
        for c, g in d.groupby(level=0):
            x = g.values; bs = [rng.choice(x, len(x)).mean() for _ in range(2000)]
            rows.append((f, m, c, len(x), x.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5)))
P = pd.DataFrame(rows, columns=["family", "metric", "condition", "n", "diff", "lo", "hi"])
P["sig"] = np.where(P.lo > 0, "better", np.where(P.hi < 0, "worse", "tie")); P.round(3).to_csv("results_v2/paired_vs_ce_tuned.csv", index=False)
print(P[P.metric == "return"].pivot(index="condition", columns="family", values="sig").to_string())
print(P[(P.metric == "min_zone_sr")].pivot(index="condition", columns="family", values="sig").to_string())
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
s = pd.read_csv("results_v2/summary.csv"); d = s[s.condition == "default"].set_index("family")
fig, ax = plt.subplots(figsize=(5.5, 4))
lam = {"ppo_lam0": 0, "ppo_lam0.5": .5, "ppo": 1, "ppo_lam2": 2, "ppo_lam4": 4}
xs = [d.loc[k, "mean_sr"] for k in lam]; ys = [d.loc[k, "min_zone_sr"] for k in lam]
ax.plot(xs, ys, "o-", label="PPO, equity weight lambda")
for k, v in lam.items(): ax.annotate(f"λ={v}", (d.loc[k, "mean_sr"], d.loc[k, "min_zone_sr"]), textcoords="offset points", xytext=(4, 4), fontsize=8)
for k, mk in [("ce_tuned", "s"), ("ppo_noequity", "^"), ("dqn", "D"), ("ppo_dr", "v")]: ax.plot(d.loc[k, "mean_sr"], d.loc[k, "min_zone_sr"], mk, label=k)
ax.set_xlabel("mean supply ratio"); ax.set_ylabel("worst-zone supply ratio"); ax.set_title("Efficiency vs fairness (default)"); ax.legend(fontsize=7); fig.tight_layout(); fig.savefig("results_v2/figs/pareto.png", dpi=150)
R = P[(P.metric == "return") & P.family.isin(["ppo", "ppo_dr", "dqn"])]
fig, ax = plt.subplots(figsize=(7, 4)); conds = sorted(R.condition.unique())
for i, f in enumerate(["ppo", "ppo_dr", "dqn"]):
    r = R[R.family == f].set_index("condition").loc[conds]
    ax.errorbar(np.arange(len(conds)) + i * .2 - .2, r["diff"], yerr=[r["diff"] - r.lo, r.hi - r["diff"]], fmt="o", label=f, capsize=2)
ax.axhline(0, color="k", lw=.8); ax.set_xticks(range(len(conds))); ax.set_xticklabels(conds, rotation=45, ha="right", fontsize=8)
ax.set_ylabel("return minus tuned fixed schedule"); ax.set_title("Where RL beats the tuned schedule (>0)"); ax.legend(fontsize=8); fig.tight_layout(); fig.savefig("results_v2/figs/regime_map.png", dpi=150)
