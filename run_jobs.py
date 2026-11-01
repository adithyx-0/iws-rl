"""Cross-platform job queue (works on macOS, Linux and Windows; replaces `xargs`).
Usage: python run_jobs.py JOBFILE [N_PARALLEL]      (default N = cores - 1)
Each non-empty, non-# line of JOBFILE is a command line of arguments to `python`, e.g.:  train_variant.py ppo 0 300000
Set IWS_V2=1 in the environment first (see docs/PLAN_v1.md). A finished job writes its model file; rerunning skips jobs whose log says done."""
import sys, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor
jobs = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
n = int(sys.argv[2]) if len(sys.argv) > 2 else max(1, (os.cpu_count() or 2) - 1)
os.makedirs("logs", exist_ok=True)
done_log = "logs/done_" + os.path.basename(sys.argv[1]) + ".txt"
done = set(open(done_log).read().splitlines()) if os.path.exists(done_log) else set()
def run(j):
    if j in done: return
    t = time.time(); r = subprocess.run([sys.executable] + j.split())
    if r.returncode == 0:
        with open(done_log, "a") as f: f.write(j + "\n")
    print(f"[{'ok' if r.returncode == 0 else 'FAILED'}] {j} ({time.time()-t:.0f}s)", flush=True)
with ThreadPoolExecutor(n) as ex: list(ex.map(run, jobs))
