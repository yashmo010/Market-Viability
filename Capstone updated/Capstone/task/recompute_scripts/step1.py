import json, numpy as np, pandas as pd, sys, types, collections, pickle
sys.path.insert(0,'.')
from src.training.label_engineering import flag_suspect_products, minmax, months_between
P=json.load(open("data/final/products_physical.json",encoding="utf-8")); R=json.load(open("data/final/reviews_physical.json",encoding="utf-8"))
ns=lambda d: types.SimpleNamespace(**d)
Pn=[ns(p) for p in P]
for r in R: r['rating']=float(r['rating']); r['review_ts']=int(r['review_ts'])
Rn=[ns(r) for r in R]
data=types.SimpleNamespace(reviews_physical=Rn,reviews_app=[],products_physical=Pn,products_app=[])
sus=flag_suspect_products(data)
print("suspect products:",len(sus), collections.Counter(x for v in sus.values() for x in v))
cnt=collections.Counter(r.product_uid for r in Rn)
rows=[]
for cat in sorted(set(p.category for p in Pn)):
    ps=[p for p in Pn if p.category==cat]
    vol=np.log1p([cnt[p.product_uid] for p in ps]); rat=np.array([p.avg_rating for p in ps],float)
    vel=np.array([cnt[p.product_uid]/max(months_between(p.first_review_ts,p.latest_review_ts),1.0) for p in ps])
    vn,rn,vl=minmax(vol),minmax(rat),minmax(vel)
    for i,p in enumerate(ps):
        rows.append(dict(product_uid=p.product_uid,category=cat,vn=vn[i],rn=rn[i],ln=vl[i],success_score=100*(.4*vn[i]+.35*rn[i]+.25*vl[i]),
                         suspect=p.product_uid in sus,n_reviews=cnt[p.product_uid],rating_count=p.rating_count,avg_rating=p.avg_rating,price=p.price,
                         brand=(p.brand or '').strip().casefold(),first_ts=p.first_review_ts,latest_ts=p.latest_review_ts,velocity=cnt[p.product_uid]/max(months_between(p.first_review_ts,p.latest_review_ts),1.0)))
L=pd.DataFrame(rows); L.to_pickle("/home/claude/R/out/labels_recomputed.pkl")
print(len(L), L.suspect.sum(), (~L.suspect).sum())
print(L[~L.suspect].groupby('category').size().to_dict())
