import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://admin-analytics-pro-1.preview.emergentagent.com').rstrip('/')

# Unique test email
TEST_EMAIL = f"test_{uuid.uuid4().hex[:6]}@test.com"
TEST_PASSWORD = "Test123456"

class TestHealth:
    """Health check tests"""
    def test_root(self):
        r = requests.get(f"{BASE_URL}/api/")
        assert r.status_code in [200, 404], f"Got {r.status_code}"
        print(f"Root response: {r.status_code}")


class TestAuth:
    """Authentication tests"""
    token = None
    user_id = None

    def test_register(self):
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "fullName": "Test User NEWME",
            "birthDate": "2000-01-01",
            "whatsapp": "081234567890",
            "userType": "individual",
            "referralSource": "google",
            "province": "Jawa Barat",
            "city": "Bandung",
            "district": "Coblong"
        }
        r = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        print(f"Register: {r.status_code} - {r.text[:200]}")
        assert r.status_code == 200
        data = r.json()
        assert data.get("success") == True
        assert "token" in data
        TestAuth.token = data["token"]
        TestAuth.user_id = data["user"]["id"]

    def test_login(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
        print(f"Login: {r.status_code} - {r.text[:200]}")
        assert r.status_code == 200
        data = r.json()
        assert data.get("success") == True
        assert "token" in data
        TestAuth.token = data["token"]

    def test_get_profile(self):
        if not TestAuth.token:
            pytest.skip("No token")
        r = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {TestAuth.token}"})
        print(f"Profile: {r.status_code} - {r.text[:200]}")
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == TEST_EMAIL


class TestAdminAuth:
    """Admin login tests"""
    admin_token = None

    def test_admin_login(self):
        r = requests.post(f"{BASE_URL}/api/admin/login", json={"email": "admin@newme.com", "password": "admin123"})
        print(f"Admin login: {r.status_code} - {r.text[:200]}")
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data or "token" in data
        TestAdminAuth.admin_token = data.get("access_token") or data.get("token")

    def test_admin_dashboard_stats(self):
        if not TestAdminAuth.admin_token:
            pytest.skip("No admin token")
        r = requests.get(
            f"{BASE_URL}/api/admin/dashboard/stats",
            headers={"Authorization": f"Bearer {TestAdminAuth.admin_token}"}
        )
        print(f"Admin stats: {r.status_code} - {r.text[:200]}")
        assert r.status_code == 200


class TestAnalytics:
    """Analytics tests"""
    def test_analytics_stats(self):
        r = requests.get(f"{BASE_URL}/api/analytics/stats")
        print(f"Analytics: {r.status_code} - {r.text[:200]}")
        assert r.status_code in [200, 401, 403]  # May require auth

    def test_analytics_with_admin_token(self):
        # Login admin first
        r = requests.post(f"{BASE_URL}/api/admin/login", json={"email": "admin@newme.com", "password": "admin123"})
        if r.status_code != 200:
            pytest.skip("Admin login failed")
        admin_token = r.json().get("access_token") or r.json().get("token")
        r2 = requests.get(
            f"{BASE_URL}/api/analytics/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Analytics with admin token: {r2.status_code} - {r2.text[:200]}")
        assert r2.status_code == 200


class TestPayments:
    """Payment tests"""
    def test_test_price(self):
        r = requests.get(f"{BASE_URL}/api/user-payments/test-price")
        print(f"Test price: {r.status_code} - {r.text[:200]}")
        assert r.status_code == 200
        data = r.json()
        assert "price" in data
        assert data["price"] == 100000  # Default Rp 100.000

    def test_admin_payments_list(self):
        r = requests.post(f"{BASE_URL}/api/admin/login", json={"email": "admin@newme.com", "password": "admin123"})
        if r.status_code != 200:
            pytest.skip("Admin login failed")
        admin_token = r.json().get("access_token") or r.json().get("token")
        r2 = requests.get(
            f"{BASE_URL}/api/admin/payment-proofs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Admin payments: {r2.status_code} - {r2.text[:200]}")
        assert r2.status_code in [200, 404]


class TestQuestions:
    """Questions/test flow tests"""
    def test_get_free_questions(self):
        if not TestAuth.token:
            # Try to login again
            r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
            if r.status_code == 200:
                TestAuth.token = r.json().get("token")
            else:
                pytest.skip("No user token")
        r = requests.get(
            f"{BASE_URL}/api/questions?testType=free",
            headers={"Authorization": f"Bearer {TestAuth.token}"}
        )
        print(f"Free questions: {r.status_code} - {r.text[:300]}")
        assert r.status_code == 200


class TestYayasan:
    """Yayasan tests"""
    def test_check_referral_nonexistent(self):
        r = requests.get(f"{BASE_URL}/api/yayasan/check-referral/TESTCODE")
        print(f"Check referral: {r.status_code} - {r.text[:200]}")
        assert r.status_code == 200
        data = r.json()
        assert data.get("isYayasan") == False

    def test_yayasan_register(self):
        yayasan_email = f"yayasan_{uuid.uuid4().hex[:6]}@test.com"
        payload = {
            "name": "Yayasan Test NEWME",
            "email": yayasan_email,
            "password": "Test123456",
            "phone": "081234567890",
            "address": "Jl. Test No 1",
            "description": "Test Yayasan"
        }
        r = requests.post(f"{BASE_URL}/api/yayasan/register", json=payload)
        print(f"Yayasan register: {r.status_code} - {r.text[:200]}")
        assert r.status_code == 200
        data = r.json()
        assert data.get("success") == True
        assert "referralCode" in data.get("yayasan", {})
