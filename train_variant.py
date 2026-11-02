"""Train one variant. Usage: python train_variant.py VARIANT SEED [STEPS]
VARIANT in: ppo, ppo_noequity, ppo_noforecast, dqn. Saves models/VARIANT_sSEED.zip"""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
import torch
torch.set_num_threads(1)
from stable_baselines3 import PPO, DQN, A2C
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from iws_env import IWSEnv
from v2cfg import BASE, MODELS

TRAIN_KW = {"ppo": {}, "dqn": {}, "ppo_noequity": {"equity_reward": False}, "ppo_noforecast": {"forecast": False},
            "ppo_long": {}, "ppo_long_noequity": {"equity_reward": False}, "ppo_long_noforecast": {"forecast": False}, "a2c": {}, "ppo_dr": {"randomize": True},
            "ppo_lam0": {"lam": 0.0}, "ppo_lam0.5": {"lam": 0.5}, "ppo_lam2": {"lam": 2.0}, "ppo_lam4": {"lam": 4.0}}

if __name__ == "__main__":
    variant, seed = sys.argv[1], int(sys.argv[2])
    steps = int(sys.argv[3]) if len(sys.argv) > 3 else 150_000
    kw = {**BASE, **TRAIN_KW[variant]}
    os.makedirs(MODELS, exist_ok=True)
    t = time.time()
    if variant == "dqn":
        env = IWSEnv(**kw)
        model = DQN("MlpPolicy", env, learning_rate=5e-4, buffer_size=100_000, learning_starts=5_000,
                    batch_size=128, gamma=0.99, train_freq=4, target_update_interval=1_000,
                    exploration_fraction=0.3, exploration_final_eps=0.05, seed=seed, verbose=0, device="cpu")
    elif variant == "a2c":
        venv = make_vec_env(lambda: IWSEnv(**kw), n_envs=8, seed=seed, vec_env_cls=DummyVecEnv)
        model = A2C("MlpPolicy", venv, n_steps=24, gamma=0.99, ent_coef=0.01, learning_rate=7e-4, seed=seed, verbose=0, device="cpu")
    else:
        venv = make_vec_env(lambda: IWSEnv(**kw), n_envs=8, seed=seed, vec_env_cls=DummyVecEnv)
        model = PPO("MlpPolicy", venv, n_steps=216, batch_size=432, n_epochs=10, gamma=0.99,
                    gae_lambda=0.95, ent_coef=0.01, learning_rate=3e-4, seed=seed, verbose=0, device="cpu")
    model.learn(steps)
    model.save(f"{MODELS}/{variant}_s{seed}")
    print(f"{variant} seed {seed} steps {steps} done in {time.time()-t:.0f}s", flush=True)
