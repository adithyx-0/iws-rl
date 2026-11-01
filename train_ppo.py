"""PPO training on IWSEnv (smoke-test scale). Usage: python train_ppo.py STEPS SEED"""
import sys, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv
from iws_env import IWSEnv
from baselines import evaluate

if __name__ == "__main__":
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    venv = make_vec_env(IWSEnv, n_envs=8, seed=seed, vec_env_cls=SubprocVecEnv)
    model = PPO("MlpPolicy", venv, n_steps=216, batch_size=432, n_epochs=10, gamma=0.99,
                gae_lambda=0.95, ent_coef=0.01, learning_rate=3e-4, seed=seed, verbose=0, device="cpu")
    t = time.time()
    chunk = steps // 5
    for i in range(5):
        model.learn(chunk, reset_num_timesteps=False)
        pol = lambda env, obs: int(model.predict(obs, deterministic=True)[0])
        m = evaluate(pol, range(10000, 10030))
        print(f"steps {(i+1)*chunk:7d} | {time.time()-t:5.0f}s | return {m['return']:.2f} meanSR {m['mean_sr']:.3f} "
              f"minZone {m['min_zone_sr']:.3f} p10 {m['p10_node_sr']:.3f} gini {m['gini_node']:.3f}", flush=True)
    model.save(f"ppo_iws_s{seed}")
