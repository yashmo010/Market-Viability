# Extra CV variants (unconstrained, repo-style early stopping) + per-category mean R2. Requires step1-3 outputs.
import json, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
src=open("step3.py").read().split("leaky=")[0]; exec(src)
leaky=["avg_rating","rating_count_log","review_velocity"]; meta=["price"]+leaky
full=meta+ASP+MR+["brand_tier","category"]; asp_only=[c for c in full if c not in leaky]
out={"asp_only_unconstrained_peek":cv(asp_only,False,True)}
d=out["asp_only_unconstrained_peek"]; d["mean_per_cat_r2"]=float(np.mean(list(d["per_cat_r2"].values())))
json.dump(out,open("res_cv_extra.json","w"),indent=1)
