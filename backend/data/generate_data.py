from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).parent / "synthetic_paimana_projects.csv"
SECTORS = ["Roads & Transport", "Water & Sanitation", "Health", "Education", "Urban Development", "Energy"]
STATES = ["Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Rajasthan", "Uttar Pradesh", "Assam", "Bihar"]
AGENCIES = ["State PWD", "Urban Development Authority", "Rural Works Department", "Municipal Corporation", "Health Infrastructure Cell"]
DRIVERS = ["Land acquisition", "Design change", "Contractor capacity", "Material price escalation", "Clearance dependency", "Monsoon disruption"]

def generate_portfolio(n: int = 180, seed: int = 42) -> pd.DataFrame:
    """Generate deterministic records shaped like a PAIMANA/CUF project extract."""
    rng = np.random.default_rng(seed); rows = []
    for i in range(n):
        sector = rng.choice(SECTORS); budget = float(rng.uniform(18, 720))
        physical = float(np.clip(rng.normal(58, 25), 4, 100)); financial = float(np.clip(physical + rng.normal(-5, 18), 2, 100)); schedule = float(np.clip(rng.normal(62, 24), 3, 100))
        delay = max(0, int((schedule - physical) * rng.uniform(1.5, 4.0) + rng.normal(5, 18))); changes = int(np.clip(rng.poisson(1.7 + delay / 60), 0, 9)); land = int(rng.random() < (0.32 if sector in ["Roads & Transport", "Urban Development"] else 0.12))
        contractor = float(np.clip(rng.normal(72 - delay * 0.25, 15), 18, 96)); inflation = float(np.clip(rng.normal(5.6, 1.5), 2, 11)); permits = int(rng.integers(0, 5))
        variance = max(0, (schedule - physical)*.38 + (financial - physical)*.24 + changes*2.7 + land*11 + (75-contractor)*.34 + inflation*.9 + rng.normal(0, 5))
        cost = float(np.clip(variance, 0, 85)); time = float(np.clip(delay / max(schedule, 1)*100 + changes*1.8 + land*9 + rng.normal(0, 5), 0, 100))
        rows.append({"project_id":f"PMN-{i+1001}","project_name":f"{sector.split(' & ')[0]} Infrastructure Package {i+1:02d}","sector":sector,"state":rng.choice(STATES),"implementing_agency":rng.choice(AGENCIES),"approved_cost_crore":round(budget,2),"physical_progress_pct":round(physical,1),"financial_progress_pct":round(financial,1),"schedule_progress_pct":round(schedule,1),"delay_days":delay,"change_orders":changes,"land_acquisition_issue":land,"contractor_health_score":round(contractor,1),"material_inflation_pct":round(inflation,1),"pending_clearances":permits,"primary_driver":rng.choice(DRIVERS),"cost_overrun_pct":round(cost,1),"time_overrun_pct":round(time,1),"status":"Completed" if physical>=98 else ("At Risk" if cost>25 or time>28 else "On Track")})
    return pd.DataFrame(rows)

def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists(): generate_portfolio().to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

if __name__ == "__main__":
    generate_portfolio().to_csv(DATA_PATH, index=False); print(f"Wrote {DATA_PATH}")
