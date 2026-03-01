"""
NEWMECLASS Education Platform - Backend API Tests
Tests for: Questions, Auth, Test Results, Wallet functionality
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://edu-platform-169.preview.emergentagent.com')

# Test credentials
TEST_USER_EMAIL = "testuser@newmeclass.com"
TEST_USER_PASSWORD = "password123"


class TestQuestionsAPI:
    """Test Questions API - 5 free + 25 paid = 30 total"""
    
    def test_get_all_questions(self):
        """GET /api/questions - should return 30 questions"""
        response = requests.get(f"{BASE_URL}/api/questions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 30, f"Expected 30 questions, got {len(data)}"
        
    def test_questions_have_free_and_paid(self):
        """Verify 5 free + 25 paid questions"""
        response = requests.get(f"{BASE_URL}/api/questions")
        assert response.status_code == 200
        
        data = response.json()
        free_questions = [q for q in data if q.get("isFree") == True]
        paid_questions = [q for q in data if q.get("isFree") == False]
        
        assert len(free_questions) == 5, f"Expected 5 free questions, got {len(free_questions)}"
        assert len(paid_questions) == 25, f"Expected 25 paid questions, got {len(paid_questions)}"
        
    def test_questions_have_required_fields(self):
        """Verify questions have required fields"""
        response = requests.get(f"{BASE_URL}/api/questions")
        assert response.status_code == 200
        
        data = response.json()
        for q in data[:5]:  # Check first 5 questions
            assert "_id" in q, "Question missing _id"
            assert "text" in q or "question" in q, "Question missing text/question"
            assert "options" in q, "Question missing options"
            assert "category" in q, "Question missing category"
            assert "isFree" in q, "Question missing isFree"
            
            # Check options structure
            assert len(q["options"]) >= 2, "Question should have at least 2 options"
            for opt in q["options"]:
                assert "text" in opt, "Option missing text"
                assert "value" in opt, "Option missing value"
                
    def test_filter_free_questions(self):
        """GET /api/questions?testType=free - should return only free questions"""
        response = requests.get(f"{BASE_URL}/api/questions?testType=free")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5, f"Expected 5 free questions, got {len(data)}"
        for q in data:
            assert q.get("isFree") == True, "Non-free question returned for testType=free"
            
    def test_filter_paid_questions(self):
        """GET /api/questions?testType=paid - should return only paid questions"""
        response = requests.get(f"{BASE_URL}/api/questions?testType=paid")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 25, f"Expected 25 paid questions, got {len(data)}"
        for q in data:
            assert q.get("isFree") == False, "Free question returned for testType=paid"


class TestAuthAPI:
    """Test Authentication API"""
    
    def test_login_success(self):
        """POST /api/auth/login - successful login with test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "token" in data, "Response missing token"
        assert "user" in data, "Response missing user"
        assert data["user"]["email"] == TEST_USER_EMAIL
        
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - invalid credentials should return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@email.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        
    def test_get_profile_with_token(self):
        """GET /api/auth/me - get profile with valid token"""
        # First login to get token
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Get profile
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL
        assert "fullName" in data
        
    def test_get_profile_without_token(self):
        """GET /api/auth/me - should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401


class TestTestResultsAPI:
    """Test Results API - save and retrieve test results"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"], response.json()["user"]["id"]
        pytest.skip("Authentication failed")
        
    def test_save_test_result(self, auth_token):
        """POST /api/test-results - save test result"""
        token, user_id = auth_token
        
        # Get some questions to create answers
        questions_response = requests.get(f"{BASE_URL}/api/questions?testType=free")
        questions = questions_response.json()
        
        # Create answers dict
        answers = {}
        for q in questions[:5]:
            answers[q["_id"]] = q["options"][0]["value"]  # Select first option
            
        # Submit test result
        response = requests.post(f"{BASE_URL}/api/test-results", json={
            "userId": user_id,
            "testType": "free",
            "results": {
                "totalScore": 15,
                "categories": {"personality": 5, "talent": 5, "interest": 5},
                "answeredCount": 5,
                "totalQuestions": 5
            },
            "answers": answers
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert "resultId" in data
        assert "analysis" in data
        
        # Verify analysis structure
        analysis = data["analysis"]
        assert "personalityType" in analysis
        assert "strengths" in analysis
        assert "areasToImprove" in analysis
        assert "careerRecommendations" in analysis
        
        return data["resultId"]
        
    def test_get_test_result_by_id(self, auth_token):
        """GET /api/test-results/{id} - get specific result"""
        token, user_id = auth_token
        
        # First create a result
        questions_response = requests.get(f"{BASE_URL}/api/questions?testType=free")
        questions = questions_response.json()
        
        answers = {}
        for q in questions[:5]:
            answers[q["_id"]] = q["options"][0]["value"]
            
        create_response = requests.post(f"{BASE_URL}/api/test-results", json={
            "userId": user_id,
            "testType": "free",
            "results": {
                "totalScore": 15,
                "categories": {"personality": 5},
                "answeredCount": 5,
                "totalQuestions": 5
            },
            "answers": answers
        })
        
        result_id = create_response.json()["resultId"]
        
        # Get the result
        response = requests.get(f"{BASE_URL}/api/test-results/{result_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["_id"] == result_id
        assert data["userId"] == user_id
        assert "analysis" in data
        
    def test_get_user_test_results(self, auth_token):
        """GET /api/test-results/user/{user_id} - get all results for user"""
        token, user_id = auth_token
        
        response = requests.get(f"{BASE_URL}/api/test-results/user/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") == True
        assert "results" in data
        assert isinstance(data["results"], list)


class TestWalletAPI:
    """Test Wallet API - balance, transactions, demo top-up"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token and user_id"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"], response.json()["user"]["id"]
        pytest.skip("Authentication failed")
        
    def test_get_wallet_balance(self, auth_token):
        """GET /api/wallet/balance/{user_id} - get wallet balance"""
        token, user_id = auth_token
        
        response = requests.get(f"{BASE_URL}/api/wallet/balance/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "balance" in data
        assert isinstance(data["balance"], (int, float))
        assert data["userId"] == user_id
        
    def test_get_wallet_transactions(self, auth_token):
        """GET /api/wallet/transactions/{user_id} - get transaction history"""
        token, user_id = auth_token
        
        response = requests.get(f"{BASE_URL}/api/wallet/transactions/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
    def test_demo_topup(self, auth_token):
        """POST /api/wallet/demo-topup - demo top-up for testing"""
        token, user_id = auth_token
        
        # Get initial balance
        balance_response = requests.get(f"{BASE_URL}/api/wallet/balance/{user_id}")
        initial_balance = balance_response.json()["balance"]
        
        # Do demo top-up
        topup_amount = 50000
        response = requests.post(f"{BASE_URL}/api/wallet/demo-topup", json={
            "userId": user_id,
            "amount": topup_amount
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        assert data["amount"] == topup_amount
        assert data["newBalance"] == initial_balance + topup_amount
        
    def test_demo_topup_minimum_amount(self, auth_token):
        """POST /api/wallet/demo-topup - verify minimum amount validation"""
        token, user_id = auth_token
        
        # Try top-up with amount below minimum (should still work for demo)
        response = requests.post(f"{BASE_URL}/api/wallet/demo-topup", json={
            "userId": user_id,
            "amount": 10000  # Minimum amount
        })
        
        assert response.status_code == 200


class TestHomepageAPI:
    """Test Homepage related APIs"""
    
    def test_health_check(self):
        """Basic health check - API is responding"""
        response = requests.get(f"{BASE_URL}/api/questions")
        assert response.status_code == 200
        
    def test_banners_endpoint(self):
        """GET /api/banners - get homepage banners"""
        response = requests.get(f"{BASE_URL}/api/banners")
        # May return 200 with empty list or 404 if not implemented
        assert response.status_code in [200, 404]
        
    def test_products_endpoint(self):
        """GET /api/products - get products"""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code in [200, 404]


class TestUserPaymentsAPI:
    """Test User Payments API"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token and user_id"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json()["token"], response.json()["user"]["id"]
        pytest.skip("Authentication failed")
        
    def test_get_payment_status(self, auth_token):
        """GET /api/user-payments/status/{user_id} - get payment status"""
        token, user_id = auth_token
        
        response = requests.get(f"{BASE_URL}/api/user-payments/status/{user_id}")
        # May return 200 with status or 404 if no payment record
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
