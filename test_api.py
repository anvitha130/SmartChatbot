import requests

BASE_URL = "http://127.0.0.1:5000"  # your Flask backend URL

def test_register_login_and_protected():
    # Register a user
    payload = {"username": "testuser", "password": "testpass"}
    r = requests.post(f"{BASE_URL}/register", json=payload)
    assert r.status_code in [200, 201, 400]  # 400 if already exists

    # Login
    r = requests.post(f"{BASE_URL}/login", json=payload)
    assert r.status_code == 200
    token = r.json().get("token")
    assert token

    # Access protected route
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/protected", headers=headers)
    assert r.status_code == 200

def test_admin_access_denied_for_user():
    payload = {"username": "testuser", "password": "testpass"}
    r = requests.post(f"{BASE_URL}/login", json=payload)
    token = r.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{BASE_URL}/admin", headers=headers)
    assert r.status_code in [401, 403]
