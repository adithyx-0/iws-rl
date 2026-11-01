"""Quick setup check (~10 s). Run: python check_setup.py"""
import sys, time, warnings
warnings.filterwarnings("ignore")
print("Python", sys.version.split()[0])
import wntr, gymnasium, stable_baselines3, torch
print("wntr", wntr.__version__, "| gymnasium", gymnasium.__version__,
      "| sb3", stable_baselines3.__version__, "| torch", torch.__version__)
from gymnasium.utils.env_checker import check_env
from iws_env import IWSEnv
env = IWSEnv()
check_env(env, skip_render_check=True)
print("check_env passed | demand nodes", env.J, "| zones", [int(m.sum()) for m in env.zone_masks])
obs, _ = env.reset(seed=0); t = time.time(); done = False
while not done:
    obs, r, done, _, info = env.step(env.action_space.n - 1)
print("one 72-hour episode: %.2fs | mean supply ratio %.3f" % (time.time() - t, info["mean_sr"]))
print("SETUP OK")
