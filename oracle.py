"""Clairvoyant open-loop oracle (hindsight upper bound). IWSEnv is deterministic given reset(seed), so for each test scenario we
optimise the whole 72-step action sequence with the cross-entropy method, warm-started from every heuristic's own action sequence
(replaying them open-loop reproduces them exactly), so oracle >= best heuristic by construction. NOT a deployable policy.
Usage: IWS_V2=1 python oracle.py [n_scenarios=30] [iters=8] [pop=48] -> {RES}/oracle.csv"""
import sys, os, warnings, time
warnings.filterwarnings("ignore")
from multiprocessing import Pool
import numpy as np, pandas as pd
from iws_env import IWSEnv
from v2cfg import BASE, RES
from baselines import all_open, make_rota, make_greedy
from eval_all import priv_greedy, ce_schedule
import glob
from stable_baselines3 import PPO
from v2cfg import MODELS

def rollout(env, seed, seq=None, policy=None):
    obs, _ = env.reset(seed=seed); R = 0.0; acts = []
    for t in range(env.H):
        a = int(seq[t]) if seq is not None else int(policy(env, obs)); acts.append(a)
        obs, r, d, _, info = env.step(a); R += r
    info["return"] = R; return R, info, acts

def solve(args):
    seed, iters, pop = args
    env = IWSEnv(**BASE); rng = np.random.default_rng(seed); H = env.H; A = env.action_space.n
    best = (-1e9, None, None); warm = []
    pols = [all_open, make_rota(1), make_greedy(1), make_greedy(2), priv_greedy, ce_schedule]
    for pth in sorted(glob.glob(f"{MODELS}/ppo_s[0-4].zip")):
        m = PPO.load(pth, device="cpu"); pols.append(lambda e, o, m=m: int(m.predict(o, deterministic=True)[0]))
    for pol in pols:
        R, info, acts = rollout(env, seed, policy=pol); warm.append(acts)
        if R > best[0]: best = (R, info, acts)
    p = np.full((H, A), 1.0 / A)
    for w in warm:
        for t, a in enumerate(w): p[t, a] += 0.5 / len(warm) * 4
    p /= p.sum(1, keepdims=True)
    # local search from the best known sequence (PPO or CE usually): random block mutations, accept if better
    cur = list(best[2]); curR = best[0]
    for k in range(150):
        c = list(cur); t0 = int(rng.integers(H)); L = int(rng.integers(1, 7))
        for t in range(t0, min(H, t0 + L)): c[t] = int(rng.integers(A)) if rng.random() < .5 else int(warm[int(rng.integers(len(warm)))][t])
        R, info, acts = rollout(env, seed, seq=c)
        if R > curR: cur, curR = c, R; best = (R, info, acts)
    for it in range(iters):
        cand = np.array([[rng.choice(A, p=p[t]) for t in range(H)] for _ in range(pop)])
        res = [rollout(env, seed, seq=c) for c in cand]
        sc = np.array([x[0] for x in res]); j = int(sc.argmax())
        if sc[j] > best[0]: best = (sc[j], res[j][1], res[j][2])
        el = cand[np.argsort(sc)[-max(2, pop // 5):]]
        f = np.zeros((H, A)); [f[np.arange(H), e].__iadd__(1) for e in el]; f /= len(el)
        p = 0.3 * p + 0.7 * f + 1e-3; p /= p.sum(1, keepdims=True)
    info = best[1]; return {"scenario": seed, "return": best[0], **{k: info[k] for k in ("mean_sr", "min_zone_sr", "p10_node_sr", "gini_node", "jain_zone", "ceiling")}}

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30; iters = int(sys.argv[2]) if len(sys.argv) > 2 else 8; pop = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    t = time.time(); os.makedirs(RES, exist_ok=True)
    with Pool(9) as P: rows = list(P.imap_unordered(solve, [(10000 + i, iters, pop) for i in range(n)]))
    df = pd.DataFrame(rows).sort_values("scenario"); df.to_csv(f"{RES}/oracle.csv", index=False)
    print(f"{n} scenarios in {time.time()-t:.0f}s"); print(df[["return", "mean_sr", "min_zone_sr", "ceiling"]].mean().round(3))
