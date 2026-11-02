"""Learning curve for PPO on the v2 environment (M3). Same hyper-parameters as train_variant.py `ppo`; the only addition is
an evaluation every EVAL_EVERY steps on 10 fixed TEST scenarios (seeds 10000-10009, never trained on), deterministic policy.
Usage: IWS_V2=1 python plots/train_curves.py SEED [STEPS=300000] [OUT_DIR=.]
Writes OUT_DIR/curve_sSEED.csv (rewritten after every evaluation, so a crash keeps the partial curve) and
OUT_DIR/curve_model_sSEED.zip (latest checkpoint). Does not touch models_v2/.
Note: same seed + same settings as train_variant.py, so the end of curve_s0/1/2 should be close to models_v2/ppo_s0/1/2."""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd, torch
torch.set_num_threads(1)
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from iws_env import IWSEnv
from v2cfg import BASE

EVAL_EVERY = 20_000
EVAL_SEEDS = range(10000, 10010)


class CurveCallback(BaseCallback):
    def __init__(self, out_csv, ckpt, eval_env):
        super().__init__(); self.out_csv, self.ckpt, self.env = out_csv, ckpt, eval_env; self.rows = []; self.next = 0

    def evaluate(self):
        R, M, W = [], [], []
        for s in EVAL_SEEDS:
            o, _ = self.env.reset(seed=s); d = False; ret = 0.0
            while not d:
                o, r, d, _, info = self.env.step(int(self.model.predict(o, deterministic=True)[0])); ret += r
            R.append(ret); M.append(info["mean_sr"]); W.append(info["min_zone_sr"])
        self.rows.append({"step": self.num_timesteps, "return": np.mean(R), "mean_sr": np.mean(M), "min_zone_sr": np.mean(W)})
        pd.DataFrame(self.rows).to_csv(self.out_csv, index=False); self.model.save(self.ckpt)
        print(f"step {self.num_timesteps} mean_sr {np.mean(M):.3f} min_zone {np.mean(W):.3f} return {np.mean(R):.2f}", flush=True)

    def _on_step(self): return True

    def _on_rollout_end(self):
        if self.num_timesteps >= self.next:
            self.evaluate(); self.next += EVAL_EVERY


if __name__ == "__main__":
    seed = int(sys.argv[1]); steps = int(sys.argv[2]) if len(sys.argv) > 2 else 300_000
    out = sys.argv[3] if len(sys.argv) > 3 else "."; os.makedirs(out, exist_ok=True)
    venv = make_vec_env(lambda: IWSEnv(**BASE), n_envs=8, seed=seed, vec_env_cls=DummyVecEnv)
    model = PPO("MlpPolicy", venv, n_steps=216, batch_size=432, n_epochs=10, gamma=0.99,
                gae_lambda=0.95, ent_coef=0.01, learning_rate=3e-4, seed=seed, verbose=0, device="cpu")
    cb = CurveCallback(os.path.join(out, f"curve_s{seed}.csv"), os.path.join(out, f"curve_model_s{seed}.zip"), IWSEnv(**BASE))
    t = time.time(); model.learn(steps, callback=cb); cb.evaluate()
    print(f"seed {seed} steps {steps} done in {time.time()-t:.0f}s", flush=True)
