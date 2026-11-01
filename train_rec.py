"""Recurrent (LSTM) PPO, optionally with domain randomisation. Usage: IWS_V2=1 python train_rec.py VARIANT SEED [STEPS]; VARIANT in rec, rec_dr -> models_v2/VARIANT_sSEED.zip"""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
import torch; torch.set_num_threads(1)
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from iws_env import IWSEnv
from v2cfg import BASE, MODELS
variant, seed = sys.argv[1], int(sys.argv[2]); steps = int(sys.argv[3]) if len(sys.argv) > 3 else 200_000
kw = {**BASE, "randomize": variant == "rec_dr"}
os.makedirs(MODELS, exist_ok=True); t = time.time()
venv = make_vec_env(lambda: IWSEnv(**kw), n_envs=8, seed=seed, vec_env_cls=DummyVecEnv)
model = RecurrentPPO("MlpLstmPolicy", venv, n_steps=144, batch_size=576, n_epochs=10, gamma=0.99, gae_lambda=0.95, ent_coef=0.01,
                     learning_rate=3e-4, seed=seed, verbose=0, device="cpu", policy_kwargs={"lstm_hidden_size": 64, "n_lstm_layers": 1})
model.learn(steps); model.save(f"{MODELS}/{variant}_s{seed}")
print(f"{variant} seed {seed} steps {steps} done in {time.time()-t:.0f}s", flush=True)
