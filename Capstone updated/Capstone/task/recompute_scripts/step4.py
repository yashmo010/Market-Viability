import json, numpy as np, pandas as pd, warnings, math, datetime as dt, collections; warnings.filterwarnings("ignore")
import xgboost as xgb
from scipy import stats
from sklearn.metrics import roc_auc_score
F=pd.read_pickle("/home/claude/R/out/features_recomputed.pkl"); F["category"]=F["category"].astype("category")
ASP=["value_for_money","utility","ease_of_use","reliability","design_appeal","after_sales","build_quality","durability","repairability"]; MR=[a+"_mention_rate" for a in ASP]
MONO={"price":-1,"brand_tier":1,**{a:1 for a in ASP}}
cols=["price"]+ASP+MR+["brand_tier","category"]
cut=int(dt.datetime(2021,10,31,23,59,59,tzinfo=dt.timezone.utc).timestamp())
F["price_pct"]=F.groupby("category").price.rank(pct=True)
res={}
def fit_predict(tr,te,cols,Fx=None):
    Fx=F if Fx is None else Fx
    p=dict(objective="reg:squarederror",learning_rate=.05,max_depth=5,min_child_weight=3,subsample=.8,colsample_bytree=.8,enable_categorical=True,tree_method="hist",random_state=42,monotone_constraints={k:v for k,v in MONO.items() if k in cols},n_estimators=600)
    X=Fx[cols]; y=Fx.success_score.values
    rng=np.random.RandomState(0); idx=rng.permutation(tr); k=int(len(idx)*.85)
    m0=xgb.XGBRegressor(**p,early_stopping_rounds=50); m0.fit(X.iloc[idx[:k]],y[idx[:k]],eval_set=[(X.iloc[idx[k:]],y[idx[k:]])],verbose=False)
    p["n_estimators"]=m0.best_iteration+1; m=xgb.XGBRegressor(**p); m.fit(X.iloc[tr],y[tr]); return m.predict(X.iloc[te])
def metrics(te,pred,Fx=None):
    Fx=F if Fx is None else Fx
    yt=Fx.success_score.values[te]; rho=stats.spearmanr(pred,yt)[0]
    lo,hi=np.percentile(yt,[20,80]); mk=(yt<=lo)|(yt>=hi); auc=roc_auc_score((yt[mk]>=hi).astype(int),pred[mk])
    cat=Fx.category.astype(str).values[te]; wc=[stats.spearmanr(pred[cat==c],yt[cat==c])[0] for c in np.unique(cat) if (cat==c).sum()>=5]
    pp=Fx.price_pct.values[te]; rho_p=stats.spearmanr(pp,yt)[0]
    pwc=[stats.spearmanr(pp[cat==c],yt[cat==c])[0] for c in np.unique(cat) if (cat==c).sum()>=5]
    return dict(rho=rho,auc=auc,within_cat_rho=float(np.mean(wc)),price_pct_rho=rho_p,price_pct_within_cat=float(np.mean(pwc)),n=len(te))
# ---- random holdout, oracle (TRUE aspects, no bridging), 117 products, 40 repeats, category-stratified
rng=np.random.RandomState(4242); reps=[]
cats=F.category.astype(str).values
for r in range(40):
    te=[]
    for c in np.unique(cats):
        ix=np.where(cats==c)[0]; k=int(round(117*len(ix)/len(F))); te+=list(rng.choice(ix,k,replace=False))
    te=np.array(te[:117]); tr=np.setdiff1d(np.arange(len(F)),te)
    reps.append(metrics(te,fit_predict(tr,te,cols)))
R=pd.DataFrame(reps); res["oracle_random_holdout_117_x40"]={k:{"mean":float(R[k].mean()),"p2.5":float(R[k].quantile(.025)),"p97.5":float(R[k].quantile(.975))} for k in ["rho","auc","within_cat_rho","price_pct_rho","price_pct_within_cat"]}
print(res["oracle_random_holdout_117_x40"],flush=True)
# ---- price baseline on all 631 (no model)
res["price_pct_vs_success_all631"]={"pooled_spearman":float(stats.spearmanr(F.price_pct,F.success_score)[0]),"by_category":{c:float(stats.spearmanr(g.price,g.success_score)[0]) for c,g in F.groupby("category")}}
# ---- temporal oracle (calendar cutoff) + brand-tier leakage check
pre=np.where(F.first_ts.values<=cut)[0]; post=np.where(F.first_ts.values>cut)[0]
m=metrics(post,fit_predict(pre,post,cols)); res["oracle_temporal_calendar"]={**m,"n_train":len(pre)}
# brand tier recomputed from TRAIN-period products only
brand_pre=collections.Counter(F.brand.values[pre]); tier=lambda n:3 if n>=11 else 2 if n>=5 else 1 if n>=2 else 0
F2=F.copy(); F2["brand_tier"]=[tier(brand_pre.get(b,0)) for b in F.brand]
m2=metrics(post,fit_predict(pre,post,cols,F2),F2); res["oracle_temporal_brand_tier_train_only"]=m2
res["brand_tier_changed_products_when_train_only"]=int((F2.brand_tier!=F.brand_tier).sum())
# 80/20 quantile split
o=np.argsort(F.first_ts.values); k=int(len(F)*.8); tr,te=o[:k],o[k:]
res["oracle_temporal_quantile80"]={**metrics(te,fit_predict(tr,te,cols)),"n_train":k}
# temporal, mature-only (>=30 reviews) post-cutoff
mat=np.array([i for i in post if F.n_reviews.values[i]>=30]); res["oracle_temporal_mature_ge30"]={**metrics(mat,fit_predict(pre,mat,cols)),"n_train":len(pre)}
print({k:res[k] for k in ["oracle_temporal_calendar","oracle_temporal_brand_tier_train_only","oracle_temporal_quantile80","oracle_temporal_mature_ge30"]},flush=True)
# ---- review-to-success correlation by category
rc={}
for c,g in F.groupby("category"):
    rs=[]; 
    for a in ASP:
        d=g[[a,"success_score"]].dropna()
        if len(d)>=10 and d[a].std()>0: rs.append(stats.pearsonr(d[a],d.success_score)[0])
    rc[c]={"mean_abs_r":float(np.mean(np.abs(rs))),"mean_r":float(np.mean(rs)),"n_aspects":len(rs)}
res["review_to_success_corr_by_category"]=rc
# ---- analytic p-values for reported (rho, n)
def pv(r,n): t=r*math.sqrt((n-2)/(1-r*r)); return float(2*stats.t.sf(abs(t),n-2))
res["p_values_analytic"]={f"rho={r}_n={n}":pv(r,n) for r,n in [(.317,59),(.545,66),(.529,118),(.529,117),(.59,125),(.59,126)]}
# Fisher-z 95% CI for reported rho (approx, for plausibility only)
def fz(r,n): z=np.arctanh(r); se=1.06/math.sqrt(n-3); return [float(np.tanh(z-1.96*se)),float(np.tanh(z+1.96*se))]
res["fisher_ci"]={f"rho={r}_n={n}":fz(r,n) for r,n in [(.317,59),(.545,66),(.529,118),(.59,125)]}
res["variance_explained_rho_sq"]={"0.529":0.529**2,"0.590":0.59**2}
json.dump(res,open("/home/claude/R/out/res_model.json","w"),indent=1,default=str)
print(json.dumps({k:res[k] for k in ["price_pct_vs_success_all631","review_to_success_corr_by_category","p_values_analytic","fisher_ci"]},indent=1))
