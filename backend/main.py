from __future__ import annotations
from contextlib import asynccontextmanager
from typing import Optional
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from data.generate_data import load_data
from ml.train import FEATURE_COLUMNS, load_models


df: pd.DataFrame|None=None; cost_model=time_model=None
@asynccontextmanager
async def lifespan(app: FastAPI):
 global df,cost_model,time_model
 df=load_data();cost_model,time_model=load_models();yield
app=FastAPI(title="PAIMANA AI API",version="1.0.0",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
def records(frame): return frame.replace({np.nan:None}).to_dict(orient="records")
def enrich(frame):
 x=frame[FEATURE_COLUMNS];out=frame.copy();out["predicted_cost_overrun_pct"]=cost_model.predict(x).round(1);out["predicted_time_overrun_pct"]=time_model.predict(x).round(1)
 out["risk_score"]=np.clip(.42*out.predicted_cost_overrun_pct+.38*out.predicted_time_overrun_pct+.12*(100-out.contractor_health_score)+.08*out.pending_clearances*6,0,100).round(0).astype(int)
 out["risk_band"]=pd.cut(out.risk_score,bins=[-1,35,60,100],labels=["Low","Medium","High"]).astype(str);return out
def alerts_for(row):
 alerts=[]
 if row.risk_score>=60: alerts.append({"severity":"Critical","message":"Composite delivery risk is above the intervention threshold."})
 if row.predicted_cost_overrun_pct>=25: alerts.append({"severity":"High","message":f"Predicted cost overrun: {row.predicted_cost_overrun_pct:.1f}%."})
 if row.delay_days>=45: alerts.append({"severity":"High","message":f"Schedule variance has reached {row.delay_days} days."})
 if row.land_acquisition_issue: alerts.append({"severity":"Medium","message":"Land acquisition dependency remains unresolved."})
 if row.contractor_health_score<55: alerts.append({"severity":"Medium","message":"Contractor health score needs a recovery review."})
 return alerts
@app.get("/api/health")
def health(): return {"status":"ok","data_mode":"synthetic"}
@app.get("/api/dashboard")
def dashboard(sector:Optional[str]=None,state:Optional[str]=None):
 data=enrich(df)
 if sector:data=data[data.sector==sector]
 if state:data=data[data.state==state]
 ranked=data.sort_values("risk_score",ascending=False)
 return {"data_notice":"Synthetic PAIMANA/CUF-style data — demonstration use only.","kpis":{"projects":len(data),"at_risk":int((data.risk_band=="High").sum()),"avg_risk":round(float(data.risk_score.mean()),1),"exposed_budget_crore":round(float(data.loc[data.risk_band=="High","approved_cost_crore"].sum()),1)},"risk_ranking":records(ranked.head(12)[["project_id","project_name","sector","state","approved_cost_crore","risk_score","risk_band","predicted_cost_overrun_pct","predicted_time_overrun_pct"]]),"sector_benchmark":records(data.groupby("sector").agg(projects=("project_id","count"),avg_risk=("risk_score","mean"),avg_cost_overrun=("predicted_cost_overrun_pct","mean"),budget=("approved_cost_crore","sum")).reset_index().round(1)),"alerts":[{"project_id":r.project_id,"project_name":r.project_name,**a} for _,r in ranked.head(35).iterrows() for a in alerts_for(r)][:10],"filters":{"sectors":sorted(df.sector.unique().tolist()),"states":sorted(df.state.unique().tolist())}}
@app.get("/api/projects")
def projects(): return records(enrich(df).sort_values("risk_score",ascending=False))
@app.get("/api/projects/{project_id}")
def project_detail(project_id:str):
 data=enrich(df);hit=data[data.project_id==project_id]
 if hit.empty: raise HTTPException(404,"Project not found")
 row=hit.iloc[0];drivers=[{"driver":"Schedule gap","impact":round(max(0,row.schedule_progress_pct-row.physical_progress_pct)*1.1,1)},{"driver":"Contractor health","impact":round(max(0,75-row.contractor_health_score)*.7,1)},{"driver":"Change orders","impact":round(row.change_orders*5.2,1)},{"driver":"Land acquisition","impact":14 if row.land_acquisition_issue else 0},{"driver":"Material inflation","impact":round(row.material_inflation_pct*1.5,1)}];peer=data[data.sector==row.sector]
 return {"project":row.to_dict(),"alerts":alerts_for(row),"drivers":sorted(drivers,key=lambda x:x["impact"],reverse=True),"benchmark":{"sector":row.sector,"peer_avg_risk":round(float(peer.risk_score.mean()),1),"peer_avg_cost_overrun":round(float(peer.predicted_cost_overrun_pct.mean()),1),"project_vs_peer_risk":round(float(row.risk_score-peer.risk_score.mean()),1)}}
@app.get("/api/assistant")
def assistant(project_id:str=Query(...),question:str=Query("")):
 detail=project_detail(project_id);p,drivers=detail["project"],detail["drivers"][:2]
 answer=f"{p['project_name']} has a {p['risk_band'].lower()} risk profile (score {p['risk_score']}/100). The model estimates {p['predicted_cost_overrun_pct']}% cost overrun and {p['predicted_time_overrun_pct']}% time overrun. The strongest drivers are {drivers[0]['driver'].lower()} and {drivers[1]['driver'].lower()}. Recommended action: assign an owner to the top driver, review the recovery plan within 14 days, and track it at the weekly PMO review."
 return {"answer":answer,"disclaimer":"Generated from synthetic prototype data; not a substitute for programme judgement."}
