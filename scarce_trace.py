import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,'.')
import numpy as np
from stable_baselines3 import PPO
from iws_env import IWSEnv
def trace(p):
    env=IWSEnv(supply_range=(0.3,0.5)); m=PPO.load(p,device="cpu"); obs,_=env.reset(seed=10000); d=False; out=[]
    while not d:
        a=int(m.predict(obs,deterministic=True)[0]); u0=env.log["delivered"]
        obs,r,d,_,i=env.step(a); out.append((a,round((env.log["delivered"]-u0)/env.day_volume*24,3)))
    return out
a=trace("models/ppo_s1.zip"); b=trace("models/ppo_noforecast_s2.zip")
print("hours with delivery>0: ",sum(x[1]>0 for x in a),sum(x[1]>0 for x in b))
print("first day, ppo_s1:",a[:24]); print("first day, nofc_s2:",b[:24])
