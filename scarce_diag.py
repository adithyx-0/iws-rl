import sys, warnings, glob, collections
warnings.filterwarnings("ignore")
sys.path.insert(0,'.')
import numpy as np
from stable_baselines3 import PPO
from iws_env import IWSEnv
for cond,kw in [("default",{}),("scarce",{"supply_range":(0.3,0.5)})]:
    for p in sorted(glob.glob("models/ppo_*.zip"))[:13]:
        nf="noforecast" in p
        env=IWSEnv(**kw, **({"forecast":False} if nf else {})); m=PPO.load(p,device="cpu")
        obs,_=env.reset(seed=10000); done=False; acts=[]; ub=None
        while not done:
            a=int(m.predict(obs,deterministic=True)[0]); acts.append(a)
            obs,r,done,_,info=env.step(a)
        print(cond,p.split('/')[-1],collections.Counter(acts).most_common(4),round(info['mean_sr'],4),round(info['budget_used'],3))
