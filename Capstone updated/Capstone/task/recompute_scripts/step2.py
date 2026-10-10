import json, numpy as np, pandas as pd, collections, datetime as dt, warnings; warnings.filterwarnings("ignore")
from scipy import stats
L=pd.read_pickle("/home/claude/R/out/labels_recomputed.pkl")
P={p['product_uid']:p for p in json.load(open("data/final/products_physical.json",encoding="utf-8"))}
R=json.load(open("data/final/reviews_physical.json",encoding="utf-8"))
ASP=["value_for_money","utility","ease_of_use","reliability","design_appeal","after_sales","build_quality","durability","repairability"]
res={}
# ---------- A. dataset ----------
res["n_reviews"]=len(R); res["n_products_total"]=len(L); res["n_suspect"]=int(L.suspect.sum()); res["n_retained"]=int((~L.suspect).sum())
res["retained_by_category"]=L[~L.suspect].groupby("category").size().to_dict()
res["total_by_category"]=L.groupby("category").size().to_dict()
nrev=L.n_reviews
res["reviews_per_product_all640"]={"min":int(nrev.min()),"p25":float(nrev.quantile(.25)),"median":float(nrev.median()),"p75":float(nrev.quantile(.75)),"max":int(nrev.max())}
rn=L[~L.suspect].n_reviews; res["reviews_per_product_retained631"]={"min":int(rn.min()),"p25":float(rn.quantile(.25)),"median":float(rn.median()),"p75":float(rn.quantile(.75)),"max":int(rn.max())}
rc=L[~L.suspect].rating_count; res["lifetime_rating_count_retained"]={"min":int(rc.min()),"p10":float(rc.quantile(.1)),"median":float(rc.median()),"p90":float(rc.quantile(.9))}
wc=np.array([int(r['word_count']) for r in R]); res["word_count"]={"min":int(wc.min()),"median":float(np.median(wc)),"max":int(wc.max())}
res["rating_distribution"]={str(k):v for k,v in sorted(collections.Counter(float(r['rating']) for r in R).items())}
ts=np.array([int(r['review_ts']) for r in R]); f=lambda t: dt.datetime.fromtimestamp(t/1000 if t>1e11 else t,dt.timezone.utc).date().isoformat()
res["review_date_range"]=[f(ts.min()),f(ts.max())]
res["price"]={"min":float(L.price.min()),"median":float(L.price.median()),"max":float(L.price.max())}
# temporal splits
cut=int(dt.datetime(2021,10,31,23,59,59,tzinfo=dt.timezone.utc).timestamp())
L["post"]=L.first_ts>cut
res["split_640"]={"pre":int((~L.post).sum()),"post":int(L.post.sum())}
C=L[~L.suspect]; res["split_631_calendar"]={"pre":int((~C.post).sum()),"post":int(C.post.sum())}
res["post_cutoff_fraud_excluded"]=int(L[L.post].suspect.sum())
post=L[L.post&~L.suspect]; res["post_clean_lt30_reviews"]=int((post.n_reviews<30).sum()); res["post_clean_mature_ge30"]=int((post.n_reviews>=30).sum())
res["post_all_lt30"]=int((L[L.post].n_reviews<30).sum())
Cs=C.sort_values("first_ts"); k=int(len(Cs)*0.8); res["quantile80_split"]={"train":k,"test":len(Cs)-k,"cutoff_date":f(Cs.first_ts.iloc[k-1])}
res["calendar_cutoff_pre_post_by_category"]={c:{"pre":int(((C.category==c)&~C.post).sum()),"post":int(((C.category==c)&C.post).sum())} for c in sorted(C.category.unique())}
# ---------- B. label ----------
res["label_std_by_category_retained"]=C.groupby("category").success_score.std(ddof=0).round(2).to_dict()
res["success_score_mean_std_retained"]=[float(C.success_score.mean()),float(C.success_score.std(ddof=0))]
res["corr_avg_rating_success"]=float(np.corrcoef(C.avg_rating,C.success_score)[0,1])
base=L.vn*.4+L.rn*.35+L.ln*.25
sens={}
for nm,w in [("vol_heavy_.5/.3/.2",(.5,.3,.2)),("rating_heavy_.3/.4/.3",(.3,.4,.3)),("equal",(1/3,1/3,1/3))]:
    alt=L.vn*w[0]+L.rn*w[1]+L.ln*w[2]; sens[nm]={"all640":float(stats.spearmanr(base,alt)[0]),"retained631":float(stats.spearmanr(base[~L.suspect],alt[~L.suspect])[0])}
res["label_weight_sensitivity_spearman"]=sens
# ---------- features (replicates feature_builder) ----------
rows=[json.loads(l) for l in open("data/extracted/aspect_scores.jsonl",encoding="utf-8") if l.strip()]
per=collections.defaultdict(lambda: collections.defaultdict(list)); nex=collections.Counter(); used=0
for r in rows:
    if r["product_type"]!="physical" or r.get("confidence",0)<0.3 or r["product_uid"] not in P: continue
    used+=1; u=r["product_uid"]; nex[u]+=1
    for a,v in r["scores"].items():
        if v is not None: per[u][a].append(v["score"])
res["extraction_rows_used_for_features"]=used
fp=collections.Counter((p['brand'] or '').strip().casefold() for p in P.values()); tier=lambda n:3 if n>=11 else 2 if n>=5 else 1 if n>=2 else 0
feat=[]
for _,r in C.iterrows():
    u=r.product_uid
    if u not in nex: continue
    d=dict(product_uid=u,category=r.category,price=float(r.price),avg_rating=r.avg_rating,rating_count_log=float(np.log1p(r.rating_count)),review_velocity=r.velocity,brand_tier=tier(fp[r.brand]),success_score=r.success_score,first_ts=r.first_ts,n_reviews=r.n_reviews,brand=r.brand)
    for a in ASP:
        v=per[u].get(a,[]); d[a]=float(np.mean(v)) if v else np.nan; d[a+"_mention_rate"]=len(v)/nex[u]
    feat.append(d)
F=pd.DataFrame(feat); F.to_pickle("/home/claude/R/out/features_recomputed.pkl"); res["n_feature_rows"]=len(F)
res["brand_tier_counts"]=F.brand_tier.value_counts().sort_index().to_dict(); res["n_distinct_brands_640"]=len(fp)
res["aspect_mention_rate_mean"]={a:float(F[a+"_mention_rate"].mean()) for a in ASP}
res["aspect_missing_products"]={a:int(F[a].isna().sum()) for a in ASP}
res["extraction_review_coverage"]={"reviews_total":len(R),"reviews_with_extraction_row":29410,"share":29410/len(R)}
json.dump(res,open("/home/claude/R/out/res_A_B.json","w"),indent=1,default=str)
print(json.dumps(res,indent=1,default=str)[:6000])
