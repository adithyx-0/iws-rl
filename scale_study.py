"""Does a per-hour source cap make zone scheduling matter? Evaluates baselines under several caps and supply levels."""
import sys, warnings; warnings.filterwarnings("ignore")
from multiprocessing import Pool
from baselines import all_open, random_policy, make_rota, make_greedy, evaluate
from eval_all import priv_greedy
P = {"all_open": all_open, "random": random_policy, "rota_k1": make_rota(1), "greedy_k1": make_greedy(1), "greedy_k2": make_greedy(2), "priv_greedy": priv_greedy}
CAPS = (1, 6, 10); SUPS = ((0.3, 0.5), (0.5, 0.9))
def job(a):
    cap, sup, name = a
    m = evaluate(P[name], range(10000, 10020), {"demand_scale": cap, "supply_range": sup})
    return cap, sup, name, m["mean_sr"], m["min_zone_sr"]
if __name__ == "__main__":
    jobs = [(c, s, n) for c in CAPS for s in SUPS for n in P]
    with Pool(9) as p: res = p.map(job, jobs)
    for c in CAPS:
        for s in SUPS:
            print(f"cap={c} supply={s}: " + "  ".join(f"{r[2]}={r[3]:.3f}/{r[4]:.3f}" for r in res if r[0] == c and r[1] == s))
