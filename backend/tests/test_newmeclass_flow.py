"""
NEWME CLASS - Complete Flow Test
Tests: Registration, Login, Free Test (1x only), Premium Test, Test Results Analysis, Top-up, Share buttons
"""
import pytest
import requests
import os
import uuid
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://yayasan-hub.preview.emergentagent.com')

# =========== TEST USER CREDENTIALS ===========
TEST_USER_EMAIL = f"test_flow_{uuid.uuid4().hex[:8]}@demo.com"
TEST_USER_PASSWORD = "test123"
TEST_USER_NAME = "Test Flow User"

class TestAuthFlow:
    """Test user registration and login flow"""
    
    def test_01_user_registration(self):
        """Test user registration with all required fields"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "fullName": TEST_USER_NAME,
            "whatsapp": "081234567890",
            "birthDate": "1990-01-15",
            "province": "DKI Jakarta",
            "city": "Jakarta Selatan",
            "district": "Kebayoran Baru"
        })
        
        print(f"Registration response: {response.status_code}")
        assert response.status_code in [200, 201], f"Registration failed: {response.text}"
        
        data = response.json()
        # Should return token or success message
        assert "token" in data or data.get("success") == True or "id" in data or "_id" in data
        print(f"Registration successful for {TEST_USER_EMAIL}")
        
        # Store token if returned
        if "token" in data:
            pytest.test_user_token = data["token"]
            pytest.test_user_id = data.get("user", {}).get("id") or data.get("user", {}).get("_id")
        else:
            pytest.test_user_token = None
            pytest.test_user_id = data.get("id") or data.get("_id") or data.get("userId")
    
    def test_02_user_login(self):
        """Test user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        print(f"Login response: {response.status_code}")
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "token" in data, "Login should return token"
        
        pytest.test_user_token = data["token"]
        user_data = data.get("user", {})
        pytest.test_user_id = user_data.get("id") or user_data.get("_id")
        
        print(f"Login successful, user_id: {pytest.test_user_id}")
        assert pytest.test_user_id is not None, "User ID should be returned"
    
    def test_03_get_user_profile(self):
        """Test getting user profile"""
        headers = {"Authorization": f"Bearer {pytest.test_user_token}"}
        response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
        
        assert response.status_code == 200, f"Get profile failed: {response.text}"
        
        data = response.json()
        assert data.get("email") == TEST_USER_EMAIL
        assert data.get("fullName") == TEST_USER_NAME
        
        # Update user ID from profile if not set
        if not pytest.test_user_id:
            pytest.test_user_id = data.get("id") or data.get("_id")
        
        print(f"Profile retrieved: {data.get('fullName')}")


class TestQuestionsAPI:
    """Test questions API with proper scoring"""
    
    def test_04_get_all_questions(self):
        """Test getting all questions"""
        response = requests.get(f"{BASE_URL}/api/questions")
        
        assert response.status_code == 200, f"Get questions failed: {response.text}"
        
        questions = response.json()
        assert isinstance(questions, list), "Should return list of questions"
        assert len(questions) >= 25, f"Should have at least 25 questions (5 free + 20 paid), got {len(questions)}"
        
        # Store questions for later tests
        pytest.all_questions = questions
        print(f"Total questions: {len(questions)}")
    
    def test_05_get_free_questions(self):
        """Test getting free test questions (5 soal)"""
        response = requests.get(f"{BASE_URL}/api/questions?testType=free")
        
        assert response.status_code == 200, f"Get free questions failed: {response.text}"
        
        questions = response.json()
        assert isinstance(questions, list)
        assert len(questions) == 5, f"Free test should have exactly 5 questions, got {len(questions)}"
        
        pytest.free_questions = questions
        print(f"Free questions count: {len(questions)}")
        
        # Verify each question has proper scores structure
        for q in questions:
            assert "options" in q, "Question should have options"
            assert q.get("isFree") == True, "Free question should have isFree=True"
            for opt in q.get("options", []):
                assert "scores" in opt, f"Option should have 'scores' dict: {opt}"
                scores = opt["scores"]
                # Check for 5 element keys
                element_keys = ["kayu", "api", "tanah", "logam", "air"]
                has_element = any(k in scores for k in element_keys)
                assert has_element, f"Option should have at least one element score: {scores}"
    
    def test_06_get_paid_questions(self):
        """Test getting paid test questions (20 soal)"""
        response = requests.get(f"{BASE_URL}/api/questions?testType=paid")
        
        assert response.status_code == 200, f"Get paid questions failed: {response.text}"
        
        questions = response.json()
        assert isinstance(questions, list)
        assert len(questions) == 20, f"Paid test should have exactly 20 questions, got {len(questions)}"
        
        pytest.paid_questions = questions
        print(f"Paid questions count: {len(questions)}")
        
        # Verify scoring structure
        for q in questions:
            assert q.get("isFree") == False, "Paid question should have isFree=False"


class TestFreeTestFlow:
    """Test free test flow - should only be available ONCE"""
    
    def test_07_check_free_test_available(self):
        """Check if free test is available for new user"""
        response = requests.get(f"{BASE_URL}/api/test-results/check-free-test/{pytest.test_user_id}")
        
        assert response.status_code == 200, f"Check free test failed: {response.text}"
        
        data = response.json()
        assert data.get("hasUsedFreeTest") == False, "New user should not have used free test yet"
        print(f"Free test available: {not data.get('hasUsedFreeTest')}")
    
    def test_08_submit_free_test_with_real_answers(self):
        """Submit free test with real answers and verify analysis"""
        # Use questions from previous test
        if not hasattr(pytest, 'free_questions') or not pytest.free_questions:
            response = requests.get(f"{BASE_URL}/api/questions?testType=free")
            pytest.free_questions = response.json()
        
        # Build answers - select options that favor specific elements
        answers = {}
        for i, q in enumerate(pytest.free_questions):
            question_id = q.get("_id")
            # Select different options to create variety in scores
            option_index = i % len(q.get("options", []))
            answers[question_id] = option_index
        
        # Submit test
        response = requests.post(f"{BASE_URL}/api/test-results", json={
            "userId": pytest.test_user_id,
            "testType": "free",
            "results": {
                "totalScore": 0,
                "categories": {},
                "answeredCount": 5,
                "totalQuestions": 5
            },
            "answers": answers
        }, headers={"Authorization": f"Bearer {pytest.test_user_token}"})
        
        print(f"Free test submit response: {response.status_code}")
        assert response.status_code == 200, f"Submit free test failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Submit should return success"
        assert "resultId" in data, "Should return resultId"
        assert "analysis" in data, "Should return analysis"
        
        # Verify analysis contains real data based on answers
        analysis = data.get("analysis", {})
        print(f"Analysis result: dominant_element={analysis.get('dominantElement')}, personality={analysis.get('personalityType')}")
        
        # CRITICAL: Verify analysis is based on real answers
        assert "dominantElement" in analysis, "Analysis should have dominant element"
        assert "personalityType" in analysis, "Analysis should have personality type"
        assert "elementScores" in analysis, "Analysis should have element scores"
        
        element_scores = analysis.get("elementScores", {})
        # At least one element should have score > 0
        total_score = sum(element_scores.values())
        assert total_score > 0, f"Element scores should be calculated from answers: {element_scores}"
        
        # Store result ID for later
        pytest.free_test_result_id = data.get("resultId")
        pytest.free_test_analysis = analysis
        print(f"Free test completed. Result ID: {pytest.free_test_result_id}")
        print(f"Element scores: {element_scores}")
    
    def test_09_verify_free_test_used(self):
        """Verify free test is now marked as used"""
        response = requests.get(f"{BASE_URL}/api/test-results/check-free-test/{pytest.test_user_id}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("hasUsedFreeTest") == True, "After completing free test, hasUsedFreeTest should be True"
        print(f"Free test marked as used: {data.get('hasUsedFreeTest')}")
    
    def test_10_get_free_test_result(self):
        """Get free test result and verify teaser content"""
        response = requests.get(
            f"{BASE_URL}/api/test-results/{pytest.free_test_result_id}",
            headers={"Authorization": f"Bearer {pytest.test_user_token}"}
        )
        
        assert response.status_code == 200, f"Get result failed: {response.text}"
        
        data = response.json()
        assert data.get("testType") == "free", "Should be free test"
        assert "analysis" in data, "Should have analysis"
        
        analysis = data.get("analysis", {})
        # Verify analysis has REAL data, not dummy
        assert analysis.get("dominantElement") in ["kayu", "api", "tanah", "logam", "air"], \
            f"Dominant element should be one of 5 elements: {analysis.get('dominantElement')}"
        assert analysis.get("personalityType") in ["Introvert", "Extrovert", "Ambivert"], \
            f"Personality type should be intro/extro/ambi: {analysis.get('personalityType')}"
        
        print(f"Free test result verified: {analysis.get('dominantElement')}, {analysis.get('personalityType')}")


class TestWalletTopUp:
    """Test wallet/top-up functionality"""
    
    def test_11_get_wallet_balance(self):
        """Get user wallet balance"""
        response = requests.get(f"{BASE_URL}/api/wallet/balance/{pytest.test_user_id}")
        
        assert response.status_code == 200, f"Get wallet failed: {response.text}"
        
        data = response.json()
        assert "balance" in data, "Should return balance"
        
        pytest.initial_balance = data.get("balance", 0)
        print(f"Initial wallet balance: {pytest.initial_balance}")
    
    def test_12_get_test_price(self):
        """Get test price from settings"""
        response = requests.get(f"{BASE_URL}/api/settings/test-price")
        
        # May return 404 if settings not configured, default to 50000
        if response.status_code == 200:
            data = response.json()
            pytest.test_price = data.get("testPrice", 50000)
        else:
            pytest.test_price = 50000
        
        print(f"Test price: {pytest.test_price}")


class TestPremiumTestFlow:
    """Test premium/paid test flow with 20 questions"""
    
    def test_13_submit_premium_test_with_real_answers(self):
        """Submit premium test with real answers (20 questions)"""
        # Get paid questions
        response = requests.get(f"{BASE_URL}/api/questions?testType=paid")
        paid_questions = response.json()
        
        assert len(paid_questions) == 20, f"Should have 20 paid questions, got {len(paid_questions)}"
        
        # Build answers - vary selections to get diverse scores
        answers = {}
        for i, q in enumerate(paid_questions):
            question_id = q.get("_id")
            # Rotate through options
            option_index = i % len(q.get("options", []))
            answers[question_id] = option_index
        
        # Submit premium test
        response = requests.post(f"{BASE_URL}/api/test-results", json={
            "userId": pytest.test_user_id,
            "testType": "paid",
            "results": {
                "totalScore": 0,
                "categories": {},
                "answeredCount": 20,
                "totalQuestions": 20
            },
            "answers": answers
        }, headers={"Authorization": f"Bearer {pytest.test_user_token}"})
        
        print(f"Premium test submit response: {response.status_code}")
        assert response.status_code == 200, f"Submit premium test failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "resultId" in data
        assert "analysis" in data
        
        pytest.premium_test_result_id = data.get("resultId")
        pytest.premium_test_analysis = data.get("analysis", {})
        
        print(f"Premium test completed. Result ID: {pytest.premium_test_result_id}")
    
    def test_14_verify_premium_analysis_complete(self):
        """Verify premium test has complete analysis"""
        response = requests.get(
            f"{BASE_URL}/api/test-results/{pytest.premium_test_result_id}",
            headers={"Authorization": f"Bearer {pytest.test_user_token}"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("testType") == "paid"
        
        analysis = data.get("analysis", {})
        
        # Premium should have more detailed analysis
        assert "dominantElement" in analysis
        assert "personalityType" in analysis
        assert "elementScores" in analysis
        
        # Check for insights (from personality_data.py)
        insights = analysis.get("insights", {})
        
        # Premium insights should include:
        # - kekuatanJatidiri (strength identity)
        # - kompilasiAdaptasi (adaptation compilation)
        # - karakter
        # - ciriKhas
        # - dibutuhkanPadaProfesi
        
        print(f"Premium analysis insights keys: {list(insights.keys())}")
        
        # Verify element scores are calculated from real answers
        element_scores = analysis.get("elementScores", {})
        total = sum(element_scores.values())
        assert total > 0, "Premium test should have calculated element scores"
        
        print(f"Premium element scores: {element_scores}")
        print(f"Dominant element: {analysis.get('dominantElement')}")
        print(f"Personality type: {analysis.get('personalityType')}")


class TestUserResults:
    """Test user results in dashboard"""
    
    def test_15_get_user_test_results(self):
        """Get all test results for user"""
        response = requests.get(f"{BASE_URL}/api/test-results/user/{pytest.test_user_id}")
        
        assert response.status_code == 200, f"Get user results failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        
        results = data.get("results", [])
        assert len(results) >= 2, f"User should have at least 2 test results (free + paid), got {len(results)}"
        
        # Verify both free and paid tests are present
        test_types = [r.get("testType") for r in results]
        assert "free" in test_types, "Should have free test result"
        assert "paid" in test_types, "Should have paid test result"
        
        print(f"User has {len(results)} test results")
    
    def test_16_get_latest_result(self):
        """Get latest test result"""
        response = requests.get(f"{BASE_URL}/api/test-results/latest/{pytest.test_user_id}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis" in data
        assert "completedAt" in data or "createdAt" in data
        
        print(f"Latest result type: {data.get('testType')}")


class TestAdminLogin:
    """Test admin functionality"""
    
    def test_17_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "email": "admin@newme.com",
            "password": "admin123"
        })
        
        print(f"Admin login response: {response.status_code}")
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        
        data = response.json()
        # Admin uses access_token
        token_key = "access_token" if "access_token" in data else "token"
        assert token_key in data, f"Admin login should return token: {data.keys()}"
        
        pytest.admin_token = data.get(token_key)
        print("Admin login successful")


class TestAnalysisAccuracy:
    """Verify test analysis is based on REAL answers, not dummy data"""
    
    def test_18_verify_different_answers_different_results(self):
        """Submit test with different answer patterns and verify different results"""
        # Get free questions
        response = requests.get(f"{BASE_URL}/api/questions?testType=free")
        questions = response.json()
        
        # Test 1: Select all first options (should favor certain elements)
        answers_pattern1 = {}
        for q in questions:
            answers_pattern1[q["_id"]] = 0  # All first options
        
        # Create new test user for pattern comparison
        test_email = f"test_pattern_{uuid.uuid4().hex[:6]}@demo.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "test123",
            "fullName": "Pattern Test User",
            "whatsapp": "081234567891",
            "birthDate": "1990-01-15",
            "province": "DKI Jakarta",
            "city": "Jakarta",
            "district": "Central"
        })
        
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": "test123"
        })
        
        if login_resp.status_code == 200:
            user_data = login_resp.json()
            user_id = user_data.get("user", {}).get("id") or user_data.get("user", {}).get("_id")
            token = user_data.get("token")
            
            # Submit with pattern 1
            resp1 = requests.post(f"{BASE_URL}/api/test-results", json={
                "userId": user_id,
                "testType": "free",
                "results": {"answeredCount": 5, "totalQuestions": 5},
                "answers": answers_pattern1
            }, headers={"Authorization": f"Bearer {token}"})
            
            if resp1.status_code == 200:
                analysis1 = resp1.json().get("analysis", {})
                
                # Now submit with all last options (different pattern)
                test_email2 = f"test_pattern2_{uuid.uuid4().hex[:6]}@demo.com"
                requests.post(f"{BASE_URL}/api/auth/register", json={
                    "email": test_email2,
                    "password": "test123",
                    "fullName": "Pattern Test User 2",
                    "whatsapp": "081234567892",
                    "birthDate": "1990-01-15",
                    "province": "DKI Jakarta",
                    "city": "Jakarta",
                    "district": "Central"
                })
                
                login_resp2 = requests.post(f"{BASE_URL}/api/auth/login", json={
                    "email": test_email2,
                    "password": "test123"
                })
                
                if login_resp2.status_code == 200:
                    user_data2 = login_resp2.json()
                    user_id2 = user_data2.get("user", {}).get("id") or user_data2.get("user", {}).get("_id")
                    token2 = user_data2.get("token")
                    
                    # All last options
                    answers_pattern2 = {}
                    for q in questions:
                        last_idx = len(q.get("options", [])) - 1
                        answers_pattern2[q["_id"]] = last_idx
                    
                    resp2 = requests.post(f"{BASE_URL}/api/test-results", json={
                        "userId": user_id2,
                        "testType": "free",
                        "results": {"answeredCount": 5, "totalQuestions": 5},
                        "answers": answers_pattern2
                    }, headers={"Authorization": f"Bearer {token2}"})
                    
                    if resp2.status_code == 200:
                        analysis2 = resp2.json().get("analysis", {})
                        
                        # Compare results - they should be DIFFERENT
                        scores1 = analysis1.get("elementScores", {})
                        scores2 = analysis2.get("elementScores", {})
                        
                        print(f"Pattern 1 (all first options): {scores1}")
                        print(f"Pattern 2 (all last options): {scores2}")
                        
                        # At least some element scores should differ
                        differ = False
                        for elem in ["kayu", "api", "tanah", "logam", "air"]:
                            if scores1.get(elem, 0) != scores2.get(elem, 0):
                                differ = True
                                break
                        
                        assert differ, "Different answer patterns should produce different results!"
                        print("VERIFIED: Different answers produce different analysis results")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
