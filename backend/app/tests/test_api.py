from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_return_classify():
    payload = {
        "return_id": "RET-102",
        "customer_id": "CUS-016",
        "order_id": "ORD-889",
        "product_id": "PRD-1234",
        "return_reason": "damaged",
        "product_category": "electronics",
        "order_value": 459.99,
        "return_window_days": 12,
        "delivery_issue": True,
        "damaged_product": True,
        "fraudulent_activity": False,
        "previous_returns": 2,
        "previous_approved_returns": 1,
        "previous_rejected_returns": 1,
        "account_risk_score": 18,
    }
    response = client.post("/api/returns/classify", json=payload)
    assert response.status_code == 200
    body = response.json()["result"]
    assert "predicted_class" in body
    assert body["probability"] >= 0


def test_workflow_stops_for_human_review_and_approval_resolves_it():
    response = client.post(
        "/api/agent/run",
        json={"user_message": "Fraudulent return claim. Suspicious repeated claims for order ORD-889."},
    )
    assert response.status_code == 200
    workflow = response.json()["workflow"]
    workflow_id = workflow["workflow_id"]
    assert workflow["workflow_status"] == "PENDING_HUMAN_REVIEW"
    assert workflow["validation_result"]["requires_human_review"] is True

    approval = client.post(
        f"/api/approval/{workflow_id}",
        json={"action": "approve", "notes": "Reviewed evidence and approved the case."},
    )
    assert approval.status_code == 200
    approved = approval.json()
    assert approved["status"] == "RESOLVED"
    assert approved["final_response"]


def test_document_ingestion_returns_real_policy_chunks():
    response = client.post("/api/documents/ingest")
    assert response.status_code == 200
    body = response.json()
    assert body["indexed"] is True
    assert body["documents"] > 0
