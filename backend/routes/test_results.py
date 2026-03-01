from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from database import get_db
from routes.auth import get_current_user
from routes.admin import verify_token as verify_admin_token
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/test-results", tags=["test-results"])
db = get_db()


class TestResultSubmission(BaseModel):
    userId: str
    testType: str  # 'free' or 'paid'
    results: dict
    answers: dict


class CategoryScore(BaseModel):
    category: str
    score: int
    maxScore: int
    percentage: float


@router.post("")
async def save_test_result(submission: TestResultSubmission):
    """Save test results after user completes a test"""
    import uuid
    try:
        # Generate analysis based on answers
        analysis = await generate_test_analysis(submission.answers, submission.testType)
        
        # Create unique result identifier to ensure no duplicates
        unique_result_id = f"{submission.userId}_{submission.testType}_{uuid.uuid4().hex[:8]}"
        
        result_data = {
            "userId": submission.userId,
            "testType": submission.testType,
            "uniqueResultId": unique_result_id,
            "totalScore": submission.results.get("totalScore", 0),
            "categories": submission.results.get("categories", {}),
            "answeredCount": submission.results.get("answeredCount", 0),
            "totalQuestions": submission.results.get("totalQuestions", 0),
            "answers": submission.answers,
            "analysis": analysis,
            "dominantElement": analysis.get("dominant_element", ""),
            "personalityType": analysis.get("personality_type", ""),
            "completedAt": datetime.utcnow(),
            "createdAt": datetime.utcnow()
        }
        
        result = await db.test_results.insert_one(result_data)
        
        return {
            "success": True,
            "resultId": str(result.inserted_id),
            "uniqueResultId": unique_result_id,
            "message": "Hasil test berhasil disimpan",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


async def generate_test_analysis(answers: dict, test_type: str) -> dict:
    """
    Generate personality analysis based on answers.
    answers format: {questionId: optionIndex}  (index 0-based)
    Questions use 'scores' dict: {"extrovert": 5, "api": 3, ...}
    """
    # Dimension accumulators
    dims = {}

    for question_id, option_index in answers.items():
        try:
            question = await db.questions.find_one({"_id": ObjectId(question_id)})
            if not question:
                continue
            options = question.get("options", [])
            # support both index-based and text-based answer
            if isinstance(option_index, int) and 0 <= option_index < len(options):
                option = options[option_index]
            else:
                # try match by text fallback
                option = next((o for o in options if o.get("text") == option_index), None)
            if not option:
                continue

            scores = option.get("scores", {})
            weight = float(question.get("weight", 1.0))
            for dim, val in scores.items():
                dims[dim] = dims.get(dim, 0) + (val * weight)
        except Exception:
            continue

    # ── Dominant element (5 Elemen) ──
    elements = {k: dims.get(k, 0) for k in ["kayu", "api", "tanah", "logam", "air"]}
    dominant_element = max(elements, key=elements.get)

    # ── Personality type (introvert vs extrovert) ──
    intro = dims.get("introvert", 0)
    extro = dims.get("extrovert", 0)
    personality_type = "Introvert" if intro >= extro else "Extrovert"
    if abs(intro - extro) < 5:
        personality_type = "Ambivert"

    # ── Dominant interest ──
    interest_keys = ["analitik", "sosial", "praktis", "artistik", "enterprising", "investigatif"]
    interests = {k: dims.get(k, 0) for k in interest_keys}
    dominant_interest = max(interests, key=interests.get)

    # ── Dominant talent ──
    talent_keys = ["komunikasi", "empati", "kinestetik", "logika", "musikal", "visual"]
    talents = {k: dims.get(k, 0) for k in talent_keys}
    dominant_talent = max(talents, key=talents.get)

    # ── Build rich insights ──
    insights = build_insights(dominant_element, personality_type, dominant_interest, dominant_talent, dims)

    return {
        "dominantElement": dominant_element,
        "personalityType": personality_type,
        "dominantInterest": dominant_interest,
        "dominantTalent": dominant_talent,
        "elementScores": elements,
        "interestScores": interests,
        "talentScores": talents,
        "allDimensions": {k: round(v, 1) for k, v in dims.items()},
        "insights": insights,
        "testType": test_type,
        # backward compat
        "dominant_element": dominant_element,
        "personality_type": personality_type,
        "strengths": insights["strengths"],
        "areasToImprove": insights["areasToImprove"],
        "careerRecommendations": insights["careerRecommendations"],
        "summary": insights["summary"],
    }


def build_insights(element: str, personality: str, interest: str, talent: str, dims: dict) -> dict:
    """Build detailed personality insights"""

    element_data = {
        "kayu": {
            "label": "KAYU (Wood)", "symbol": "🌿",
            "desc": "Kreatif, penuh visi, inovatif, dan selalu mencari pertumbuhan.",
            "kekuatan": ["Kreativitas tinggi", "Pemikiran visioner", "Inovasi & ide segar", "Kemampuan memulai hal baru"],
            "tantangan": ["Sulit menyelesaikan sesuatu", "Mudah terdistraksi", "Terlalu idealis"],
        },
        "api": {
            "label": "API (Fire)", "symbol": "🔥",
            "desc": "Penuh semangat, karismatik, pemimpin alami, dan energik.",
            "kekuatan": ["Kepemimpinan natural", "Semangat menular", "Kemampuan motivasi", "Berani mengambil risiko"],
            "tantangan": ["Mudah terbakar emosi", "Impulsif", "Sulit sabar"],
        },
        "tanah": {
            "label": "TANAH (Earth)", "symbol": "🌍",
            "desc": "Stabil, dapat diandalkan, praktis, dan berorientasi pada fakta.",
            "kekuatan": ["Sangat bisa diandalkan", "Konsistensi tinggi", "Praktis & realistis", "Stabilitas emosi"],
            "tantangan": ["Sulit berubah", "Terlalu konservatif", "Cenderung kaku"],
        },
        "logam": {
            "label": "LOGAM (Metal)", "symbol": "⚡",
            "desc": "Adaptif, komunikatif, fleksibel, dan pandai bergaul.",
            "kekuatan": ["Mudah beradaptasi", "Komunikasi excellent", "Network luas", "Fleksibel & kreatif"],
            "tantangan": ["Kurang fokus", "Mudah bosan", "Tidak konsisten"],
        },
        "air": {
            "label": "AIR (Water)", "symbol": "💧",
            "desc": "Bijaksana, intuitif, reflektif, dan memiliki empati mendalam.",
            "kekuatan": ["Kebijaksanaan mendalam", "Intuisi tajam", "Empati tinggi", "Pemikir strategis"],
            "tantangan": ["Terlalu introspektif", "Sulit membuat keputusan cepat", "Overthinking"],
        },
    }

    interest_careers = {
        "analitik": ["Data Scientist", "Financial Analyst", "Business Analyst", "Research Scientist", "Statistician"],
        "sosial": ["Konselor/Psikolog", "HR Manager", "Social Worker", "Teacher/Trainer", "Community Manager"],
        "praktis": ["Engineer", "Dokter/Perawat", "Chef/Culinary", "Teknisi", "Arsitek"],
        "artistik": ["Graphic Designer", "Musisi/Seniman", "Content Creator", "UX/UI Designer", "Fotografer"],
        "enterprising": ["Entrepreneur", "Sales Manager", "Marketing Director", "Business Development", "CEO/Founder"],
        "investigatif": ["Peneliti/Scientist", "Programmer/Developer", "Dokter Spesialis", "Detektif/Investigator", "Profesor"],
    }

    talent_descriptions = {
        "komunikasi": "kemampuan berbicara dan menyampaikan ide secara efektif",
        "empati": "kepekaan tinggi terhadap perasaan dan kebutuhan orang lain",
        "kinestetik": "koordinasi fisik dan kecerdasan gerakan yang unggul",
        "logika": "kemampuan berpikir sistematis dan memecahkan masalah kompleks",
        "musikal": "kepekaan terhadap ritme, nada, dan ekspresi musikal",
        "visual": "kemampuan visualisasi, estetika, dan desain yang kuat",
    }

    el = element_data.get(element, element_data["air"])
    careers = interest_careers.get(interest, ["Profesional di bidang yang diminati"])
    talent_desc = talent_descriptions.get(talent, talent)

    summary = (
        f"Anda adalah pribadi dengan karakter dominan {el['label']} — {el['desc']} "
        f"Sebagai seorang {personality}, Anda lebih suka {('bekerja sendiri dan merenung' if personality == 'Introvert' else 'berkolaborasi dan berinteraksi')}. "
        f"Bakat terkuat Anda adalah {talent_desc}."
    )

    return {
        "elementLabel": el["label"],
        "elementSymbol": el["symbol"],
        "elementDescription": el["desc"],
        "personalityLabel": personality,
        "strengths": el["kekuatan"],
        "areasToImprove": el["tantangan"],
        "careerRecommendations": careers,
        "talentDescription": talent_desc,
        "summary": summary,
    }


def get_personality_insights(category_analysis: dict, dominant_category: str) -> dict:
    """Get personality insights based on analysis"""
    
    insights = {
        "personality": {
            "type": "Analitis & Reflektif",
            "strengths": [
                "Kemampuan introspeksi yang kuat",
                "Pengambilan keputusan yang matang",
                "Kepekaan terhadap perasaan diri dan orang lain",
                "Kemampuan beradaptasi dengan situasi"
            ],
            "areasToImprove": [
                "Lebih berani mengambil risiko",
                "Meningkatkan kepercayaan diri",
                "Lebih asertif dalam menyampaikan pendapat"
            ],
            "careerRecommendations": [
                "Psikolog atau Konselor",
                "Peneliti atau Analis",
                "Penulis atau Content Creator",
                "Human Resources",
                "Trainer atau Coach"
            ],
            "summary": "Anda memiliki kepribadian yang mendalam dan reflektif. Kemampuan memahami diri sendiri adalah kekuatan utama Anda."
        },
        "talent": {
            "type": "Kreatif & Inovatif",
            "strengths": [
                "Bakat kepemimpinan yang natural",
                "Kemampuan menciptakan ide baru",
                "Skill dalam memecahkan masalah kompleks",
                "Kemampuan memotivasi tim"
            ],
            "areasToImprove": [
                "Lebih sabar dalam proses",
                "Mendengarkan pendapat orang lain",
                "Fokus pada detail"
            ],
            "careerRecommendations": [
                "Entrepreneur atau Founder",
                "Creative Director",
                "Product Manager",
                "Konsultan Bisnis",
                "Marketing Strategist"
            ],
            "summary": "Anda memiliki bakat alami dalam kepemimpinan dan inovasi. Ide-ide kreatif adalah kekuatan utama Anda."
        },
        "skills": {
            "type": "Terorganisir & Sistematis",
            "strengths": [
                "Kemampuan manajemen waktu yang baik",
                "Detail-oriented dan teliti",
                "Konsisten dalam menyelesaikan tugas",
                "Kemampuan komunikasi yang efektif"
            ],
            "areasToImprove": [
                "Lebih fleksibel terhadap perubahan",
                "Berani keluar dari zona nyaman",
                "Lebih spontan dalam situasi tertentu"
            ],
            "careerRecommendations": [
                "Project Manager",
                "Akuntan atau Auditor",
                "Data Analyst",
                "Operations Manager",
                "Quality Assurance"
            ],
            "summary": "Anda memiliki kemampuan organisasi yang luar biasa. Sistematis dan terstruktur adalah ciri khas Anda."
        },
        "interest": {
            "type": "Sosial & Empatik",
            "strengths": [
                "Empati yang tinggi",
                "Kemampuan membangun relasi",
                "Peduli terhadap kesejahteraan orang lain",
                "Kemampuan kolaborasi tim"
            ],
            "areasToImprove": [
                "Lebih tegas dalam mengambil keputusan",
                "Mengelola batasan personal",
                "Fokus pada tujuan pribadi"
            ],
            "careerRecommendations": [
                "Pekerja Sosial",
                "Guru atau Dosen",
                "Customer Success Manager",
                "Community Manager",
                "Healthcare Professional"
            ],
            "summary": "Anda memiliki jiwa sosial yang kuat. Kemampuan memahami dan membantu orang lain adalah kekuatan utama Anda."
        }
    }
    
    return insights.get(dominant_category, insights["personality"])


@router.get("/{result_id}")
async def get_test_result(result_id: str):
    """Get specific test result by ID"""
    try:
        if not ObjectId.is_valid(result_id):
            raise HTTPException(status_code=400, detail="Invalid result ID")
        
        result = await db.test_results.find_one({"_id": ObjectId(result_id)})
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        result["_id"] = str(result["_id"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_test_results(user_id: str, limit: int = 10):
    """Get all test results for a specific user"""
    try:
        cursor = db.test_results.find({"userId": user_id}).sort("completedAt", -1).limit(limit)
        results = await cursor.to_list(length=limit)
        
        for r in results:
            r["_id"] = str(r["_id"])
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/latest/{user_id}")
async def get_latest_result(user_id: str, test_type: Optional[str] = None):
    """Get the latest test result for a user"""
    try:
        query = {"userId": user_id}
        if test_type:
            query["testType"] = test_type
        
        result = await db.test_results.find_one(query, sort=[("completedAt", -1)])
        
        if not result:
            raise HTTPException(status_code=404, detail="No test results found")
        
        result["_id"] = str(result["_id"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



@router.get("/check-free-test/{user_id}")
async def check_free_test_usage(user_id: str):
    """Check if user has already used their free test"""
    try:
        # Check if user has any free test results
        free_test = await db.test_results.find_one({
            "userId": user_id,
            "testType": "free"
        })
        
        # Also check user's freeTestStatus
        user = None
        if ObjectId.is_valid(user_id):
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        user_completed_free = False
        if user:
            user_completed_free = user.get("freeTestStatus") == "completed"
        
        has_used = free_test is not None or user_completed_free
        
        return {
            "hasUsedFreeTest": has_used,
            "message": "Test gratis sudah digunakan" if has_used else "Test gratis tersedia"
        }
    except Exception as e:
        return {
            "hasUsedFreeTest": False,
            "message": f"Error checking: {str(e)}"
        }


# ========== Admin Endpoints for Premium Results ==========

@router.get("/admin/premium-results")
async def get_all_premium_results(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    token_data: dict = Depends(verify_admin_token)
):
    """Get all premium test results (admin only)"""
    try:
        query = {"testType": "paid"}
        
        cursor = db.test_results.find(query).sort("completedAt", -1).skip(skip).limit(limit)
        results = await cursor.to_list(length=limit)
        
        # Enrich with user data
        enriched_results = []
        for r in results:
            r["_id"] = str(r["_id"])
            
            # Get user info
            if ObjectId.is_valid(r.get("userId")):
                user = await db.users.find_one({"_id": ObjectId(r["userId"])})
                if user:
                    r["userName"] = user.get("fullName", "Unknown")
                    r["userEmail"] = user.get("email", "")
                    r["userWhatsapp"] = user.get("whatsapp", "")
                    
                    # Skip if search doesn't match
                    if search:
                        search_lower = search.lower()
                        if (search_lower not in r["userName"].lower() and 
                            search_lower not in r["userEmail"].lower()):
                            continue
            
            enriched_results.append(r)
        
        return {
            "success": True,
            "count": len(enriched_results),
            "results": enriched_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/admin/premium-results/{user_id}")
async def get_user_premium_result(
    user_id: str,
    token_data: dict = Depends(verify_admin_token)
):
    """Get premium test result for specific user (admin only)"""
    try:
        result = await db.test_results.find_one({
            "userId": user_id,
            "testType": "paid"
        }, sort=[("completedAt", -1)])
        
        if not result:
            raise HTTPException(status_code=404, detail="Hasil test premium tidak ditemukan")
        
        result["_id"] = str(result["_id"])
        
        # Get user info
        if ObjectId.is_valid(user_id):
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                result["userName"] = user.get("fullName", "Unknown")
                result["userEmail"] = user.get("email", "")
                result["userWhatsapp"] = user.get("whatsapp", "")
                result["userProvince"] = user.get("province", "")
                result["userCity"] = user.get("city", "")
        
        # Get AI analysis if exists
        ai_analysis = await db.ai_analyses.find_one({
            "userId": user_id,
            "testType": "paid"
        }, sort=[("createdAt", -1)])
        
        if ai_analysis:
            result["aiAnalysis"] = ai_analysis.get("aiAnalysis", {})
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/admin/stats")
async def get_test_results_stats(
    token_data: dict = Depends(verify_admin_token)
):
    """Get test results statistics (admin only)"""
    try:
        total_free = await db.test_results.count_documents({"testType": "free"})
        total_paid = await db.test_results.count_documents({"testType": "paid"})
        
        # Get recent results
        recent = await db.test_results.find(
            {"testType": "paid"}
        ).sort("completedAt", -1).limit(5).to_list(5)
        
        for r in recent:
            r["_id"] = str(r["_id"])
            if ObjectId.is_valid(r.get("userId")):
                user = await db.users.find_one({"_id": ObjectId(r["userId"])})
                if user:
                    r["userName"] = user.get("fullName", "Unknown")
        
        return {
            "totalFree": total_free,
            "totalPaid": total_paid,
            "total": total_free + total_paid,
            "recentPremium": recent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
