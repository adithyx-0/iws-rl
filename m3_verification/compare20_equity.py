"""Quick 20-seed check: PPO vs baselines, default condition, scenarios 10000-10019. Paired by scenario."""
import warnings; warnings.filterwarnings("ignore")
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import glob, numpy as np, torch
torch.set_num_threads(1)
from stable_baselines3 import PPO
from iws_env import IWSEnv
from v2cfg import BASE
from eval_all import baseline_policy, CONDITIONS
import sys
SEEDS = range(10000, 10020)
def run(pol, kw):
    env = IWSEnv(**{**BASE, **kw}); out = []
    for s in SEEDS:
        o, _ = env.reset(seed=s); d = False
        while not d:
            o, r, t, tr, info = env.step(pol(env, o)); d = t or tr
        out.append((info["mean_sr"], info["min_zone_sr"]))
    return np.array(out)
models = [PPO.load(p, device="cpu") for p in sorted(glob.glob("models/ppo_long_s*.zip"))]
names = ["random","greedy_k1","priv_greedy_k1","ce_schedule"]
print("WORST-ZONE supply ratio (min_zone_sr), mean over 20 scenarios; diffs are PPO minus baseline, paired, 95% CI")
print(f"{'condition':13s}" + "".join(f"{n:>15s}" for n in ["random","greedy_k1","priv_greedy","ce_sched","PPO"]) + "   PPO-greedy_k1 [CI]    PPO-ce [CI]    PPO-priv [CI]", flush=True)
for cond, (kw, _) in CONDITIONS.items():
    r = {n: run(baseline_policy(n), kw)[:,1] for n in names}
    pm = np.mean([run(lambda e,o,m=m: int(m.predict(o, deterministic=True)[0]), kw)[:,1] for m in models], 0)
    def ci(a):
        d = pm - a; se = d.std(ddof=1)/np.sqrt(len(d)); return f"{d.mean():+.3f}[{d.mean()-1.96*se:+.3f},{d.mean()+1.96*se:+.3f}]"
    print(f"{cond:13s}" + "".join(f"{v.mean():15.3f}" for v in [r['random'],r['greedy_k1'],r['priv_greedy_k1'],r['ce_schedule'],pm]) + "  " + ci(r['greedy_k1']) + " " + ci(r['ce_schedule']) + " " + ci(r['priv_greedy_k1']), flush=True)
