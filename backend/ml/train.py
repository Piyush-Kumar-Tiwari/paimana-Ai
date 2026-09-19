from __future__ import annotations
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from data.generate_data import load_data

MODEL_DIR = Path(__file__).parent / "artifacts"
FEATURE_COLUMNS = ["approved_cost_crore","physical_progress_pct","financial_progress_pct","schedule_progress_pct","delay_days","change_orders","land_acquisition_issue","contractor_health_score","material_inflation_pct","pending_clearances"]
def train_models():
    df=load_data(); x=df[FEATURE_COLUMNS]; metrics={}; MODEL_DIR.mkdir(exist_ok=True)
    for target,filename in [("cost_overrun_pct","cost_model.pkl"),("time_overrun_pct","time_model.pkl")]:
        xt,xv,yt,yv=train_test_split(x,df[target],test_size=.22,random_state=42); model=RandomForestRegressor(n_estimators=180,max_depth=9,min_samples_leaf=2,random_state=42); model.fit(xt,yt); pred=model.predict(xv)
        metrics[target]={"mae":round(float(mean_absolute_error(yv,pred)),2),"r2":round(float(r2_score(yv,pred)),2)}
        with open(MODEL_DIR/filename,"wb") as out: pickle.dump(model,out)
    return metrics
def load_models():
    if not (MODEL_DIR/"cost_model.pkl").exists(): train_models()
    with open(MODEL_DIR/"cost_model.pkl","rb") as f: cost=pickle.load(f)
    with open(MODEL_DIR/"time_model.pkl","rb") as f: time=pickle.load(f)
    return cost,time
if __name__=="__main__": print(train_models())
