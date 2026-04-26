import sys
import os
import requests
import uuid
sys.path.append("c:\\sgac")

from infrastructure.security.jwt_service import JWTService
from uuid import uuid4

jwt_service = JWTService()
token = jwt_service.create_token(
    user_id="842e9ddc-7764-4ba6-ac74-d2a52272a30e",
    rut="12345678-9",
    full_name="Test User",
    role="admin"
)

url = "http://127.0.0.1:8005/api/activities/"
headers = {"Authorization": f"Bearer {token}"}
payload = {
    "title": "Test Activity",
    "day": 15,
    "priority_id": 1,
    "description": "Some description",
    "emoji": "🚀",
    "checklist": []
}

resp = requests.post(url, json=payload, headers=headers)
print("Status:", resp.status_code)
print("Response:", resp.text)
