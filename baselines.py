"""Baseline policies for IWSEnv. Each policy: f(env, obs) -> action int."""
import numpy as np
from iws_env import IWSEnv


def encode(open_z):
    return int(sum(int(b) << z for z, b in enumerate(open_z)))


def all_open(env, obs):
    return env.action_space.n - 1


def random_policy(env, obs):
    return int(env.np_random.integers(env.action_space.n))


def make_rota(k):
    """Fixed rota: k zones open at a time, cycling every hour block of 24/Z*k hours (utility practice)."""
    def pol(env, obs):
        h = env.t % 24
        block = 24 // env.Z
        start = (h // block) % env.Z
        open_z = np.zeros(env.Z, bool)
        for i in range(k):
            open_z[(start + i) % env.Z] = True
        return encode(open_z)
    pol.__name__ = f"rota_k{k}"
    return pol


def make_greedy(k):
    """Most-deprived-first: open the k zones with the lowest supply ratio so far today (uses obs only)."""
    def pol(env, obs):
        sr = obs[2:4 * env.Z:4]                 # zone supply ratio so far today
        hrs = obs[3:4 * env.Z:4]                # hours since last supply (tie-break)
        order = np.lexsort((-hrs, sr))
        open_z = np.zeros(env.Z, bool); open_z[order[:k]] = True
        return encode(open_z)
    pol.__name__ = f"greedy_k{k}"
    return pol


def evaluate(policy, seeds, env_kwargs=None):
    env = IWSEnv(**(env_kwargs or {}))
    out = []
    for s in seeds:
        obs, _ = env.reset(seed=int(s)); done = False; R = 0.0
        while not done:
            obs, r, done, _, info = env.step(policy(env, obs)); R += r
        info["return"] = R
        out.append(info)
    keys = ["return", "mean_sr", "min_zone_sr", "p10_node_sr", "gini_node"]
    return {k: float(np.mean([o[k] for o in out])) for k in keys}


if __name__ == "__main__":
    import sys, time
    seeds = range(10000, 10030)
    pols = [random_policy, all_open] + [make_rota(k) for k in (1, 2, 3)] + [make_greedy(k) for k in (1, 2, 3)]
    print(f"{'policy':12s} {'return':>8s} {'meanSR':>7s} {'minZone':>8s} {'p10node':>8s} {'gini':>6s}")
    for p in pols:
        t = time.time(); m = evaluate(p, seeds)
        print(f"{p.__name__:12s} {m['return']:8.2f} {m['mean_sr']:7.3f} {m['min_zone_sr']:8.3f} "
              f"{m['p10_node_sr']:8.3f} {m['gini_node']:6.3f}  ({time.time()-t:.0f}s)")
