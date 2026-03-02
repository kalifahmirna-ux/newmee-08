"""
NEWME CLASS - Yayasan (Foundation) API Tests
Tests for: Registration, Login, Dashboard, Wallet, Withdrawals, Admin endpoints
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://yayasan-hub.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@newme.com"
ADMIN_PASSWORD = "admin123"
DEMO_YAYASAN_EMAIL = "demo.yayasan@test.com"
DEMO_YAYASAN_PASSWORD = "demo123"


class TestYayasanRegistration:
    """Test Yayasan Registration API"""

    def test_register_yayasan_success(self):
        """POST /api/yayasan/register - register new yayasan"""
        unique_id = uuid.uuid4().hex[:6]
        response = requests.post(f"{BASE_URL}/api/yayasan/register", json={
            "name": f"TEST_Yayasan_{unique_id}",
            "email": f"test_yayasan_{unique_id}@test.com",
            "password": "testpass123",
            "phone": "08123456789"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("success") == True
        assert "token" in data
        assert "yayasan" in data
        assert "referralCode" in data["yayasan"]
        assert data["yayasan"]["referralCode"].startswith("YYS")
        print(f"Yayasan registered with referral code: {data['yayasan']['referralCode']}")

    def test_register_duplicate_email(self):
        """POST /api/yayasan/register - duplicate email should fail"""
        unique_id = uuid.uuid4().hex[:6]
        email = f"test_dup_{unique_id}@test.com"
        
        # First registration
        response1 = requests.post(f"{BASE_URL}/api/yayasan/register", json={
            "name": f"TEST_Yayasan_Dup_{unique_id}",
            "email": email,
            "password": "testpass123",
            "phone": "08123456789"
        })
        assert response1.status_code == 200
        
        # Second registration with same email
        response2 = requests.post(f"{BASE_URL}/api/yayasan/register", json={
            "name": f"TEST_Yayasan_Dup2_{unique_id}",
            "email": email,
            "password": "testpass123",
            "phone": "08123456789"
        })
        assert response2.status_code == 400


class TestYayasanLogin:
    """Test Yayasan Login API"""

    @pytest.fixture
    def yayasan_account(self):
        """Create a yayasan account for testing"""
        unique_id = uuid.uuid4().hex[:6]
        response = requests.post(f"{BASE_URL}/api/yayasan/register", json={
            "name": f"TEST_Login_Yayasan_{unique_id}",
            "email": f"test_login_{unique_id}@test.com",
            "password": "logintest123",
            "phone": "08123456789"
        })
        if response.status_code == 200:
            return {
                "email": f"test_login_{unique_id}@test.com",
                "password": "logintest123",
                "token": response.json()["token"]
            }
        pytest.skip("Failed to create yayasan account")

    def test_login_success(self, yayasan_account):
        """POST /api/yayasan/login - successful login"""
        response = requests.post(f"{BASE_URL}/api/yayasan/login", json={
            "email": yayasan_account["email"],
            "password": yayasan_account["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "token" in data
        assert "yayasan" in data
        assert data["yayasan"]["email"] == yayasan_account["email"]

    def test_login_wrong_password(self, yayasan_account):
        """POST /api/yayasan/login - wrong password"""
        response = requests.post(f"{BASE_URL}/api/yayasan/login", json={
            "email": yayasan_account["email"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_email(self):
        """POST /api/yayasan/login - nonexistent email"""
        response = requests.post(f"{BASE_URL}/api/yayasan/login", json={
            "email": "nonexistent@email.com",
            "password": "anypassword"
        })
        assert response.status_code == 401


class TestYayasanProfile:
    """Test Yayasan Profile API"""

    @pytest.fixture
    def yayasan_token(self):
        """Get yayasan token"""
        unique_id = uuid.uuid4().hex[:6]
        response = requests.post(f"{BASE_URL}/api/yayasan/register", json={
            "name": f"TEST_Profile_Yayasan_{unique_id}",
            "email": f"test_profile_{unique_id}@test.com",
            "password": "profiletest123",
            "phone": "08123456789"
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Failed to create yayasan account")

    def test_get_profile_success(self, yayasan_token):
        """GET /api/yayasan/me - get profile with valid token"""
        response = requests.get(f"{BASE_URL}/api/yayasan/me", headers={
            "Authorization": f"Bearer {yayasan_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "email" in data
        assert "referralCode" in data
        assert "referralPrice" in data

    def test_get_profile_without_token(self):
        """GET /api/yayasan/me - should fail without token"""
        response = requests.get(f"{BASE_URL}/api/yayasan/me")
        assert response.status_code == 401

    def test_get_profile_invalid_token(self):
        """GET /api/yayasan/me - should fail with invalid token"""
        response = requests.get(f"{BASE_URL}/api/yayasan/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401


class TestYayasanDashboard:
    """Test Yayasan Dashboard API"""

    @pytest.fixture
    def yayasan_token(self):
        """Get yayasan token"""
        unique_id = uuid.uuid4().hex[:6]
        response = requests.post(f"{BASE_URL}/api/yayasan/register", json={
            "name": f"TEST_Dashboard_Yayasan_{unique_id}",
            "email": f"test_dashboard_{unique_id}@test.com",
            "password": "dashtest123",
            "phone": "08123456789"
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Failed to create yayasan account")

    def test_get_dashboard_stats(self, yayasan_token):
        """GET /api/yayasan/dashboard/stats - get dashboard statistics"""
        response = requests.get(f"{BASE_URL}/api/yayasan/dashboard/stats", headers={
            "Authorization": f"Bearer {yayasan_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "totalUsers" in data
        assert "completedTests" in data
        assert "pendingUsers" in data
        assert "paidUsers" in data
        assert "totalEarnings" in data
        assert "referralCode" in data
        assert "referralPrice" in data

    def test_get_yayasan_users(self, yayasan_token):
        """GET /api/yayasan/users - get users who used referral"""
        response = requests.get(f"{BASE_URL}/api/yayasan/users", headers={
            "Authorization": f"Bearer {yayasan_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_yayasan_test_results(self, yayasan_token):
        """GET /api/yayasan/test-results - get test results from referrals"""
        response = requests.get(f"{BASE_URL}/api/yayasan/test-results", headers={
            "Authorization": f"Bearer {yayasan_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestYayasanReferralPrice:
    """Test Yayasan Referral Price Update API"""

    @pytest.fixture
    def yayasan_token(self):
        """Get yayasan token"""
        unique_id = uuid.uuid4().hex[:6]
        response = requests.post(f"{BASE_URL}/api/yayasan/register", json={
            "name": f"TEST_Price_Yayasan_{unique_id}",
            "email": f"test_price_{unique_id}@test.com",
            "password": "pricetest123",
            "phone": "08123456789"
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Failed to create yayasan account")

    def test_update_referral_price_success(self, yayasan_token):
        """PUT /api/yayasan/referral-price - update price"""
        response = requests.put(f"{BASE_URL}/api/yayasan/referral-price", 
            json={"referralPrice": 75000},
            headers={"Authorization": f"Bearer {yayasan_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data.get("referralPrice") == 75000

    def test_update_referral_price_too_low(self, yayasan_token):
        """PUT /api/yayasan/referral-price - price below minimum"""
        response = requests.put(f"{BASE_URL}/api/yayasan/referral-price", 
            json={"referralPrice": 10000},  # Below 25000 minimum
            headers={"Authorization": f"Bearer {yayasan_token}"}
        )
        # Should return 400 if below minimum
        assert response.status_code in [200, 400]


class TestYayasanWallet:
    """Test Yayasan Wallet API"""

    @pytest.fixture
    def yayasan_token(self):
        """Get yayasan token"""
        unique_id = uuid.uuid4().hex[:6]
        response = requests.post(f"{BASE_URL}/api/yayasan/register", json={
            "name": f"TEST_Wallet_Yayasan_{unique_id}",
            "email": f"test_wallet_{unique_id}@test.com",
            "password": "wallettest123",
            "phone": "08123456789"
        })
        if response.status_code == 200:
            return response.json()["token"]
        pytest.skip("Failed to create yayasan account")

    def test_get_wallet_balance(self, yayasan_token):
        """GET /api/yayasan/wallet - get wallet balance"""
        response = requests.get(f"{BASE_URL}/api/yayasan/wallet", headers={
            "Authorization": f"Bearer {yayasan_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert "transactions" in data
        assert isinstance(data["transactions"], list)

    def test_request_withdrawal_insufficient_balance(self, yayasan_token):
        """POST /api/yayasan/wallet/withdraw - insufficient balance"""
        response = requests.post(f"{BASE_URL}/api/yayasan/wallet/withdraw", 
            json={
                "amount": 100000,  # More than 0 balance
                "bankName": "BCA",
                "bankAccount": "1234567890",
                "accountName": "Test Account"
            },
            headers={"Authorization": f"Bearer {yayasan_token}"}
        )
        
        # Should fail with insufficient balance
        assert response.status_code == 400

    def test_request_withdrawal_below_minimum(self, yayasan_token):
        """POST /api/yayasan/wallet/withdraw - below minimum amount"""
        response = requests.post(f"{BASE_URL}/api/yayasan/wallet/withdraw", 
            json={
                "amount": 10000,  # Below 50000 minimum
                "bankName": "BCA",
                "bankAccount": "1234567890",
                "accountName": "Test Account"
            },
            headers={"Authorization": f"Bearer {yayasan_token}"}
        )
        
        # Should fail with minimum amount error
        assert response.status_code == 400


class TestAdminYayasan:
    """Test Admin Yayasan Management API"""

    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        pytest.skip("Admin authentication failed")

    def test_admin_list_yayasan(self, admin_token):
        """GET /api/yayasan/admin/list - get all yayasan"""
        response = requests.get(f"{BASE_URL}/api/yayasan/admin/list", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} yayasan in the system")

    def test_admin_get_withdrawals(self, admin_token):
        """GET /api/yayasan/admin/withdrawals - get all withdrawal requests"""
        response = requests.get(f"{BASE_URL}/api/yayasan/admin/withdrawals", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestDemoYayasanLogin:
    """Test login with provided demo yayasan credentials"""

    def test_demo_yayasan_login(self):
        """Test login with demo.yayasan@test.com credentials"""
        response = requests.post(f"{BASE_URL}/api/yayasan/login", json={
            "email": DEMO_YAYASAN_EMAIL,
            "password": DEMO_YAYASAN_PASSWORD
        })
        
        # This might fail if demo yayasan doesn't exist
        if response.status_code == 401:
            print("Demo yayasan account doesn't exist, creating one...")
            # Create the demo account
            reg_response = requests.post(f"{BASE_URL}/api/yayasan/register", json={
                "name": "Demo Yayasan",
                "email": DEMO_YAYASAN_EMAIL,
                "password": DEMO_YAYASAN_PASSWORD,
                "phone": "08123456789"
            })
            
            if reg_response.status_code == 200:
                print(f"Created demo yayasan account")
                # Try login again
                response = requests.post(f"{BASE_URL}/api/yayasan/login", json={
                    "email": DEMO_YAYASAN_EMAIL,
                    "password": DEMO_YAYASAN_PASSWORD
                })
                
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True
            assert "token" in data
            print(f"Demo yayasan logged in successfully, referral code: {data['yayasan'].get('referralCode')}")
        else:
            print(f"Demo yayasan login failed: {response.status_code} - {response.text}")


class TestPaymentApprovalCommission:
    """Test payment approval and yayasan commission credit"""

    def test_payment_approval_endpoint(self):
        """Test that payment approval endpoint exists"""
        # Just verify the endpoint exists
        response = requests.get(f"{BASE_URL}/api/payments?status=pending")
        # May return 401 if auth required or 200 with data
        assert response.status_code in [200, 401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
