"""Gate 1: oracle vs PPO vs baselines on the same 30 test scenarios (v2 default). Usage: IWS_V2=1 python gate1.py"""
import numpy as np, pandas as pd
from v2cfg import RES
o = pd.read_csv(f"{RES}/oracle.csv").set_index("scenario"); ep = pd.read_csv(f"{RES}/episodes.csv")
ep = ep[(ep.condition == "default") & ep.scenario.isin(o.index)]
ep["family"] = ep.method.str.replace(r"_s\d+$", "", regex=True)
per = ep.groupby(["family", "scenario"])[["return", "mean_sr", "min_zone_sr"]].mean().reset_index()
print(f"{'method':16s} {'mean_sr':>8s} {'gap_to_oracle':>14s} {'min_zone':>9s} {'gap':>7s}")
rows = [("ORACLE", o.mean_sr.mean(), 0, o.min_zone_sr.mean(), 0)]
for f, g in per.groupby("family"):
    g = g.set_index("scenario"); rows.append((f, g.mean_sr.mean(), (o.mean_sr - g.mean_sr).mean(), g.min_zone_sr.mean(), (o.min_zone_sr - g.min_zone_sr).mean()))
for r in sorted(rows, key=lambda r: -r[1]): print(f"{r[0]:16s} {r[1]:8.3f} {r[2]:14.3f} {r[3]:9.3f} {r[4]:7.3f}")
base = [r for r in rows if r[0] not in ("ORACLE", "ppo")]; b = max(base, key=lambda r: r[1])
print(f"\nceiling (mean) {o.ceiling.mean():.3f}; best non-PPO method {b[0]} {b[1]:.3f}; oracle headroom over it: mean {o.mean_sr.mean()-b[1]:.3f}, worst-zone {o.min_zone_sr.mean()-max(r[3] for r in base):.3f}")
print("GATE 1:", "PASS (headroom)" if (o.mean_sr.mean() - b[1] >= 0.02 or o.min_zone_sr.mean() - max(r[3] for r in base) >= 0.05) else "FAIL (no headroom -> C2+C3 core)")

r = ep.groupby(["family", "scenario"])["return"].mean().unstack(0); r["oracle"] = o["return"]
print("\nreturn (the objective): " + ", ".join(f"{k} {v:.2f}" for k, v in r.mean().sort_values(ascending=False).items() if k in ("oracle", "ppo", "ce_schedule", "random", "greedy_k2")))
print(f"oracle - ppo return: {(r.oracle - r.ppo).mean():.3f} (>=0 by construction if the oracle is valid); oracle - ce: {(r.oracle - r.ce_schedule).mean():.3f}")
