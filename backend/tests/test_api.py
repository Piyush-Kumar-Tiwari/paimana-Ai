from fastapi.testclient import TestClient
from main import app
def test_dashboard_and_project_detail():
 with TestClient(app) as client:
  response=client.get("/api/dashboard");assert response.status_code==200;payload=response.json();assert payload["kpis"]["projects"]==180;assert len(payload["risk_ranking"])>0
  detail=client.get(f"/api/projects/{payload['risk_ranking'][0]['project_id']}");assert detail.status_code==200;assert "drivers" in detail.json()
