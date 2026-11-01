"""Does opening all zones at once starve the network hydraulically? hyd_fill = delivered/requested (1.0 = hydraulics never limit)."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
from iws_env import IWSEnv
for scale in (1, 3, 6, 10, 15):
    row = []
    for name, act in (("all-open", 15), ("1 zone", 1)):
        env = IWSEnv(demand_scale=scale, supply_range=(1.5, 1.5), tank_days=(0.05, 0.05), alpha=4.0)
        fills, pm = [], []
        for sd in range(3):
            env.reset(seed=sd); d = False
            while not d: _, _, d, _, info = env.step(act); pm.append(env.last_p[env.last_p > 0].mean() if (env.last_p > 0).any() else np.nan)
            fills.append(info["hyd_fill"])
        row.append(f"{name}: fill={np.mean(fills):.2f} pressure={np.nanmean(pm):.0f}m")
    print(f"demand_scale={scale:2d}  " + " | ".join(row))
