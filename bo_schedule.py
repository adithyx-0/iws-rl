"""Open-loop optimised daily valve schedule (stand-in for the Bayesian-optimisation schedules in the IWS literature).
A schedule is a 24 x Z bit matrix repeated every day. Optimised with the cross-entropy method on TRAIN scenarios (seeds 0-9),
objective = mean episode return of IWSEnv (same reward the RL agents see). Saves results/ce_schedule.npy.
Usage: python bo_schedule.py [iters] [pop]"""
import sys, warnings, time
warnings.filterwarnings("ignore")
from multiprocessing import Pool
import numpy as np
from iws_env import IWSEnv

SEEDS = list(range(10))
_env = None

def score(bits):
    global _env
    if _env is None: _env = IWSEnv()
    R = 0.0
    for s in SEEDS:
        obs, _ = _env.reset(seed=s); done = False
        while not done:
            h = _env.t % 24
            a = int(sum(int(b) << z for z, b in enumerate(bits[h])))
            obs, r, done, _, _ = _env.step(a); R += r
    return R / len(SEEDS)

if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    pop = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    Z = 4; rng = np.random.default_rng(0)
    p = np.full((24, Z), 0.3); best = (-1e9, None); t = time.time()
    with Pool(5) as pool:
        for it in range(iters):
            cand = (rng.random((pop, 24, Z)) < p).astype(int)
            sc = np.array(pool.map(score, list(cand)))
            elite = cand[np.argsort(sc)[-pop // 5:]]
            p = 0.3 * p + 0.7 * elite.mean(0); p = np.clip(p, 0.03, 0.97)
            if sc.max() > best[0]: best = (sc.max(), cand[sc.argmax()])
            print(f"iter {it} mean {sc.mean():.2f} best {sc.max():.2f} overall {best[0]:.2f} ({time.time()-t:.0f}s)", flush=True)
    np.save("results/ce_schedule.npy", best[1]); print(best[1].T)
