from fastapi.testclient import TestClient
import sys
import os
sys.path.append("c:\\sgac")

from main import app
from presentation.api.dependencies import get_current_user
from uuid import uuid4

def override_get_current_user():
    return {"user_id": str(uuid4()), "username": "test"}

app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)
resp = client.post("/api/activities/", json={
    "title": "Test Activity",
    "day": 15,
    "priority_id": 1,
    "description": "Some description",
    "emoji": "🚀",
    "checklist": []
})
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
