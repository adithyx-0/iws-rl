"""Quick 20-seed check: PPO vs baselines, default condition, scenarios 10000-10019. Paired by scenario."""
import warnings; warnings.filterwarnings("ignore")
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import glob, numpy as np, torch
torch.set_num_threads(1)
from stable_baselines3 import PPO
from iws_env import IWSEnv
from v2cfg import BASE
from eval_all import baseline_policy
SEEDS = range(10000, 10020)
def run(pol):
    env = IWSEnv(**BASE); out = []
    for s in SEEDS:
        o, _ = env.reset(seed=s); d = False
        while not d:
            o, r, t, tr, info = env.step(pol(env, o)); d = t or tr
        out.append((info["mean_sr"], info["min_zone_sr"]))
    return np.array(out)
res = {n: run(baseline_policy(n)) for n in ["random", "greedy_k1", "greedy_k2", "priv_greedy_k1", "ce_schedule"]}
ppo = []
for p in sorted(glob.glob("models/ppo_long_s*.zip")):
    m = PPO.load(p, device="cpu"); ppo.append(run(lambda e, o: int(m.predict(o, deterministic=True)[0])))
res["ppo_long (5 seeds avg)"] = np.mean(ppo, 0)
pm = res["ppo_long (5 seeds avg)"][:, 0]
print(f"{'method':24s} {'mean_sr':>8s} {'worst_zone':>10s} {'PPO diff':>9s} {'95% CI':>18s} {'PPO wins':>8s}")
for n, a in res.items():
    d = pm - a[:, 0]; se = d.std(ddof=1) / np.sqrt(len(d))
    print(f"{n:24s} {a[:,0].mean():8.3f} {a[:,1].mean():10.3f} {d.mean():+9.3f} [{d.mean()-1.96*se:+.3f},{d.mean()+1.96*se:+.3f}] {(d>0).sum():5d}/20")
