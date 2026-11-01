"""IWS_V2=1 switches every script to the harder environment (demand_scale=8: hydraulics bind) with separate models_v2/ and results_v2/."""
import os
V2 = os.environ.get("IWS_V2") == "1"
BASE = {"demand_scale": 8.0} if V2 else {}
MODELS = "models_v2" if V2 else "models"
RES = "results_v2" if V2 else "results"
