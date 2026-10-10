import json, time, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
import xgboost as xgb
from sklearn.model_selection import KFold
from sklearn.metrics import *
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
F=pd.read_pickle("/home/claude/R/out/features_recomputed.pkl"); y=F.success_score.values
ASP=["value_for_money","utility","ease_of_use","reliability","design_appeal","after_sales","build_quality","durability","repairability"]
MR=[a+"_mention_rate" for a in ASP]
F["category"]=F["category"].astype("category")
MONO={"price":-1,"brand_tier":1,**{a:1 for a in ASP}}
P0=dict(objective="reg:squarederror",n_estimators=600,learning_rate=.05,max_depth=5,min_child_weight=3,subsample=.8,colsample_bytree=.8,enable_categorical=True,tree_method="hist",random_state=42)
def params(cols,mono=True):
    p=dict(P0); c={k:v for k,v in MONO.items() if k in cols}
    if mono and c: p["monotone_constraints"]=c
    return p
def cv(cols,mono=True,peek=True,n_fixed=None):
    """peek=True replicates repo: early stopping evaluated on the validation fold."""
    X=F[cols]; kf=KFold(5,shuffle=True,random_state=42); r2=[];rm=[];ma=[];oof=np.zeros(len(F)); its=[]
    for tr,va in kf.split(X):
        if peek:
            m=xgb.XGBRegressor(**params(cols,mono),early_stopping_rounds=50); m.fit(X.iloc[tr],y[tr],eval_set=[(X.iloc[va],y[va])],verbose=False); its.append(m.best_iteration+1)
        else:
            # honest: early stopping on an inner split of the TRAIN fold only
            rng=np.random.RandomState(0); idx=rng.permutation(tr); k=int(len(idx)*.85); itr,iva=idx[:k],idx[k:]
            m0=xgb.XGBRegressor(**params(cols,mono),early_stopping_rounds=50); m0.fit(X.iloc[itr],y[itr],eval_set=[(X.iloc[iva],y[iva])],verbose=False)
            nb=m0.best_iteration+1; its.append(nb); pp=params(cols,mono); pp["n_estimators"]=nb
            m=xgb.XGBRegressor(**pp); m.fit(X.iloc[tr],y[tr],verbose=False)
        p=m.predict(X.iloc[va]); oof[va]=p; r2.append(r2_score(y[va],p)); rm.append(np.sqrt(mean_squared_error(y[va],p))); ma.append(mean_absolute_error(y[va],p))
    pc={}
    for c in F.category.cat.categories:
        mk=(F.category==c).values; pc[c]=float(r2_score(y[mk],oof[mk]))
    return dict(r2=float(np.mean(r2)),r2_sd=float(np.std(r2)),rmse=float(np.mean(rm)),mae=float(np.mean(ma)),best_iter=int(np.mean(its)),per_cat_r2=pc)
leaky=["avg_rating","rating_count_log","review_velocity"]
meta=["price"]+leaky
full=meta+ASP+MR+["brand_tier","category"]
asp_only=[c for c in full if c not in leaky]              # repo "aspects-only" (keeps price)
no_price=[c for c in asp_only if c!="price"]
pure=[c for c in no_price if c!="brand_tier"]
out={}
for nm,cols in [("FULL (incl. rating/count/velocity)",full),("ASPECTS-ONLY (repo headline: aspects+mention+price+brand_tier+category)",asp_only),("aspects+brand_tier (no price)",no_price),("pure aspects (no price, no brand_tier)",pure)]:
    out[nm]={"repo_style_peek_constrained":cv(cols,True,True),"honest_constrained":cv(cols,True,False),"honest_unconstrained":cv(cols,False,False)}
    print(nm,{k:round(v["r2"],3) for k,v in out[nm].items()},flush=True)
json.dump(out,open("/home/claude/R/out/res_cv.json","w"),indent=1)
# ---- Table 1 replication (exact script config) ----
meta_cols={"price","avg_rating","rating_count_log","review_velocity","category"}
manifest=meta+ASP+MR+["brand_tier","category"]
tcols=[c for c in manifest if c not in meta_cols]
X=np.nan_to_num(F[tcols].values.astype(float),nan=0.0)
def models():
    return {"XGBoost":xgb.XGBRegressor(n_estimators=600,max_depth=5,learning_rate=.05,min_child_weight=3,subsample=.8,colsample_bytree=.8,tree_method="hist",random_state=42,early_stopping_rounds=50),
    "Random Forest":RandomForestRegressor(n_estimators=600,max_depth=10,min_samples_leaf=3,random_state=42,n_jobs=-1),
    "Gradient Boosting":GradientBoostingRegressor(n_estimators=600,max_depth=5,learning_rate=.05,min_samples_leaf=3,subsample=.8,random_state=42),
    "SVR (RBF)":SVR(kernel="rbf",C=10,epsilon=.1),"Ridge Regression":Ridge(alpha=1.0,random_state=42),
    "MLP Regressor":MLPRegressor(hidden_layer_sizes=(128,64),max_iter=500,learning_rate_init=.001,early_stopping=True,random_state=42)}
def tb(yv,q=5):
    th=np.percentile(yv,[100/q,100*(q-1)/q]); bot=yv<=th[0]; top=yv>=th[1]; lab=np.zeros(len(yv),int); lab[top]=1; return bot|top,lab
T={}
for variant in ("repo_exact","no_val_peek"):
    for name,model in models().items():
        if variant=="no_val_peek" and name!="XGBoost": continue
        kf=KFold(5,shuffle=True,random_state=42); M={k:[] for k in("r2","rmse","mae","acc","prec","rec","f1","spec","auc","mcc","time")}; cm=np.zeros((2,2),int)
        for tr,va in kf.split(X):
            t0=time.perf_counter()
            if name=="XGBoost" and variant=="repo_exact": model.fit(X[tr],y[tr],eval_set=[(X[va],y[va])],verbose=False)
            elif name=="XGBoost":
                m2=xgb.XGBRegressor(n_estimators=600,max_depth=5,learning_rate=.05,min_child_weight=3,subsample=.8,colsample_bytree=.8,tree_method="hist",random_state=42,early_stopping_rounds=50)
                rng=np.random.RandomState(0); idx=rng.permutation(tr); k=int(len(idx)*.85); m2.fit(X[idx[:k]],y[idx[:k]],eval_set=[(X[idx[k:]],y[idx[k:]])],verbose=False)
                nb=m2.best_iteration+1; model=xgb.XGBRegressor(n_estimators=nb,max_depth=5,learning_rate=.05,min_child_weight=3,subsample=.8,colsample_bytree=.8,tree_method="hist",random_state=42); model.fit(X[tr],y[tr])
            else: model.fit(X[tr],y[tr])
            M["time"].append(time.perf_counter()-t0); p=model.predict(X[va]); yv=y[va]
            M["r2"].append(r2_score(yv,p)); M["rmse"].append(np.sqrt(mean_squared_error(yv,p))); M["mae"].append(mean_absolute_error(yv,p))
            mk,lab=tb(yv)
            if mk.sum()>=4 and len(np.unique(lab[mk]))==2:
                pb=(p[mk]>=np.median(yv)).astype(int); M["acc"].append(accuracy_score(lab[mk],pb)); M["prec"].append(precision_score(lab[mk],pb,zero_division=0)); M["rec"].append(recall_score(lab[mk],pb,zero_division=0)); M["f1"].append(f1_score(lab[mk],pb,zero_division=0)); M["mcc"].append(matthews_corrcoef(lab[mk],pb))
                c=confusion_matrix(lab[mk],pb,labels=[0,1]); cm+=c; M["spec"].append(c[0,0]/(c[0,0]+c[0,1])); M["auc"].append(roc_auc_score(lab[mk],p[mk]))
        T[f"{name} [{variant}]"]={**{k:float(np.mean(v)) for k,v in M.items()},"r2_sd":float(np.std(M["r2"])),"cm":cm.tolist()}
        print(name,variant,round(np.mean(M["r2"]),3),round(np.mean(M["auc"]),3),flush=True)
json.dump(T,open("/home/claude/R/out/res_table1.json","w"),indent=1)
