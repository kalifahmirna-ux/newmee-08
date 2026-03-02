from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.question import Question, QuestionCreate, QuestionUpdate, Banner
from database import get_db
from datetime import datetime
from bson import ObjectId
from routes.admin import verify_token

router = APIRouter(prefix="/api/questions", tags=["questions"])
db = get_db()

# Questions Endpoints
@router.get("", response_model=List[dict])
async def get_questions(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    testType: Optional[str] = None,  # 'free' or 'paid'
    isActive: Optional[bool] = None
):
    """
    Get all questions
    testType: 'free' for basic questions (limit 5), 'paid' for all questions
    """
    try:
        query = {}
        if category:
            query["category"] = category
        
        # Handle isActive - if True, include questions where isActive is True OR not set
        if isActive is True:
            query["$or"] = [{"isActive": True}, {"isActive": {"$exists": False}}]
        elif isActive is False:
            query["isActive"] = False
        
        # Map testType to isFree field
        if testType:
            if testType == 'free':
                query["isFree"] = True
            elif testType == 'paid':
                query["isFree"] = False
        
        cursor = db.questions.find(query).skip(skip).limit(limit).sort("order", 1)
        questions = await cursor.to_list(length=limit)
        
        # Convert and add testType field for frontend compatibility
        for question in questions:
            question["_id"] = str(question["_id"])
            # Add testType field based on isFree
            question["testType"] = "free" if question.get("isFree", False) else "paid"
            # Ensure text field exists (frontend uses 'text', seed uses 'question')
            if "question" in question and "text" not in question:
                question["text"] = question["question"]
        
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/{question_id}", response_model=dict)
async def get_question(question_id: str):
    """
    Get question by ID
    """
    try:
        if not ObjectId.is_valid(question_id):
            raise HTTPException(status_code=400, detail="Invalid question ID")
        
        question = await db.questions.find_one({"_id": ObjectId(question_id)})
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        question["_id"] = str(question["_id"])
        return question
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("", response_model=dict)
async def create_question(
    question: QuestionCreate,
    token_data: dict = Depends(verify_token)
):
    """
    Create new question (admin only)
    """
    try:
        question_data = question.dict()
        question_data["isActive"] = True
        question_data["createdAt"] = datetime.utcnow()
        question_data["updatedAt"] = datetime.utcnow()
        
        result = await db.questions.insert_one(question_data)
        
        return {
            "success": True,
            "questionId": str(result.inserted_id),
            "message": "Question created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{question_id}", response_model=dict)
async def update_question(
    question_id: str,
    updates: QuestionUpdate,
    token_data: dict = Depends(verify_token)
):
    """
    Update question (admin only)
    """
    try:
        if not ObjectId.is_valid(question_id):
            raise HTTPException(status_code=400, detail="Invalid question ID")
        
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updatedAt"] = datetime.utcnow()
        
        result = await db.questions.update_one(
            {"_id": ObjectId(question_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {"success": True, "message": "Question updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{question_id}", response_model=dict)
async def delete_question(
    question_id: str,
    token_data: dict = Depends(verify_token)
):
    """
    Delete question (admin only)
    """
    try:
        if not ObjectId.is_valid(question_id):
            raise HTTPException(status_code=400, detail="Invalid question ID")
        
        result = await db.questions.delete_one({"_id": ObjectId(question_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {"success": True, "message": "Question deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/categories/list", response_model=List[str])
async def get_question_categories():
    """
    Get all question categories
    """
    try:
        categories = await db.questions.distinct("category")
        return categories if categories else ["personality", "talent", "skills", "interest"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/reorder", response_model=dict)
async def reorder_questions(
    orders: List[dict],
    token_data: dict = Depends(verify_token)
):
    """
    Reorder questions (admin only)
    orders: [{"id": "...", "order": 1}, ...] or [{"questionId": "...", "order": 1}, ...]
    """
    try:
        for item in orders:
            # Support both 'id' and 'questionId' keys
            question_id = item.get("id") or item.get("questionId")
            order = item.get("order", 0)
            
            if question_id and ObjectId.is_valid(question_id):
                await db.questions.update_one(
                    {"_id": ObjectId(question_id)},
                    {"$set": {"order": order}}
                )
        
        return {"success": True, "message": "Questions reordered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/seed-questions")
async def seed_questions():
    """Seed default questions - 5 free + 20 paid with proper dimension scoring"""
    try:
        # Delete existing questions and re-seed
        await db.questions.delete_many({})
        
        # 5 Free Questions dengan scoring ke 5 Elemen + Personality Dimensions
        free_questions = [
            {
                "text": "Ketika menghadapi masalah, saya lebih suka:",
                "question": "Ketika menghadapi masalah, saya lebih suka:",
                "category": "personality",
                "options": [
                    {"text": "Menganalisis secara logis dan sistematis", "value": "A", "scores": {"logam": 5, "introvert": 3, "analitik": 4, "logika": 4}},
                    {"text": "Mengikuti intuisi dan perasaan", "value": "B", "scores": {"air": 5, "introvert": 4, "artistik": 3, "empati": 4}},
                    {"text": "Berdiskusi dengan orang lain", "value": "C", "scores": {"api": 4, "extrovert": 5, "sosial": 5, "komunikasi": 4}},
                    {"text": "Mencoba berbagai solusi langsung", "value": "D", "scores": {"tanah": 5, "extrovert": 3, "praktis": 5, "kinestetik": 4}}
                ],
                "order": 1,
                "isFree": True,
                "isActive": True,
                "weight": 1.5,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Dalam situasi sosial, saya cenderung:",
                "question": "Dalam situasi sosial, saya cenderung:",
                "category": "personality",
                "options": [
                    {"text": "Menjadi pusat perhatian dan aktif berbicara", "value": "A", "scores": {"api": 5, "extrovert": 5, "sosial": 5, "komunikasi": 5}},
                    {"text": "Mendengarkan dan mengamati lebih banyak", "value": "B", "scores": {"air": 5, "introvert": 5, "investigatif": 4, "empati": 3}},
                    {"text": "Bergantung pada situasi dan suasana", "value": "C", "scores": {"kayu": 4, "extrovert": 2, "introvert": 2, "artistik": 3}},
                    {"text": "Memilih berinteraksi dengan kelompok kecil", "value": "D", "scores": {"logam": 4, "introvert": 4, "sosial": 2, "empati": 4}}
                ],
                "order": 2,
                "isFree": True,
                "isActive": True,
                "weight": 1.5,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Saat bekerja dalam tim, peran yang paling cocok untuk saya adalah:",
                "question": "Saat bekerja dalam tim, peran yang paling cocok untuk saya adalah:",
                "category": "talent",
                "options": [
                    {"text": "Pemimpin yang mengarahkan", "value": "A", "scores": {"api": 5, "extrovert": 5, "enterprising": 5, "komunikasi": 4}},
                    {"text": "Kreator ide dan inovasi", "value": "B", "scores": {"kayu": 5, "introvert": 3, "artistik": 5, "visual": 4}},
                    {"text": "Pelaksana yang detail", "value": "C", "scores": {"tanah": 5, "introvert": 3, "praktis": 5, "logika": 4}},
                    {"text": "Mediator yang menjaga harmoni", "value": "D", "scores": {"air": 5, "extrovert": 2, "sosial": 4, "empati": 5}}
                ],
                "order": 3,
                "isFree": True,
                "isActive": True,
                "weight": 1.5,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Kegiatan yang paling menarik bagi saya adalah:",
                "question": "Kegiatan yang paling menarik bagi saya adalah:",
                "category": "interest",
                "options": [
                    {"text": "Membaca dan mempelajari hal baru", "value": "A", "scores": {"air": 5, "introvert": 5, "investigatif": 5, "logika": 4}},
                    {"text": "Berkreasi dan membuat sesuatu", "value": "B", "scores": {"kayu": 5, "introvert": 3, "artistik": 5, "visual": 5}},
                    {"text": "Berolahraga dan aktivitas fisik", "value": "C", "scores": {"tanah": 5, "extrovert": 3, "praktis": 4, "kinestetik": 5}},
                    {"text": "Bersosialisasi dan membantu orang lain", "value": "D", "scores": {"api": 5, "extrovert": 5, "sosial": 5, "empati": 5}}
                ],
                "order": 4,
                "isFree": True,
                "isActive": True,
                "weight": 1.5,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Ketika mengambil keputusan penting, saya lebih mengandalkan:",
                "question": "Ketika mengambil keputusan penting, saya lebih mengandalkan:",
                "category": "personality",
                "options": [
                    {"text": "Data dan fakta yang jelas", "value": "A", "scores": {"logam": 5, "introvert": 3, "analitik": 5, "logika": 5}},
                    {"text": "Perasaan dan nilai-nilai personal", "value": "B", "scores": {"api": 4, "introvert": 4, "sosial": 3, "empati": 5}},
                    {"text": "Saran dari orang yang dipercaya", "value": "C", "scores": {"tanah": 4, "extrovert": 4, "sosial": 4, "komunikasi": 3}},
                    {"text": "Pengalaman masa lalu", "value": "D", "scores": {"air": 5, "introvert": 4, "praktis": 4, "investigatif": 3}}
                ],
                "order": 5,
                "isFree": True,
                "isActive": True,
                "weight": 1.5,
                "createdAt": datetime.utcnow()
            }
        ]
        
        # 20 Paid Questions dengan scoring ke 5 Elemen + Personality Dimensions
        paid_questions = [
            {
                "text": "Bagaimana cara Anda mengelola stres?",
                "question": "Bagaimana cara Anda mengelola stres?",
                "category": "personality",
                "options": [
                    {"text": "Berolahraga atau aktivitas fisik", "value": "A", "scores": {"tanah": 5, "extrovert": 3, "kinestetik": 5, "praktis": 4}},
                    {"text": "Meditasi atau relaksasi", "value": "B", "scores": {"air": 5, "introvert": 5, "investigatif": 3, "empati": 3}},
                    {"text": "Berbicara dengan orang terdekat", "value": "C", "scores": {"api": 4, "extrovert": 5, "sosial": 5, "komunikasi": 4}},
                    {"text": "Fokus menyelesaikan sumber stres", "value": "D", "scores": {"logam": 5, "introvert": 3, "analitik": 5, "logika": 4}}
                ],
                "order": 6,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Dalam berkomunikasi, saya lebih efektif dengan:",
                "question": "Dalam berkomunikasi, saya lebih efektif dengan:",
                "category": "skills",
                "options": [
                    {"text": "Tulisan yang terstruktur", "value": "A", "scores": {"logam": 5, "introvert": 4, "analitik": 4, "logika": 4}},
                    {"text": "Presentasi visual", "value": "B", "scores": {"kayu": 5, "extrovert": 3, "artistik": 5, "visual": 5}},
                    {"text": "Diskusi langsung", "value": "C", "scores": {"api": 5, "extrovert": 5, "sosial": 5, "komunikasi": 5}},
                    {"text": "Demonstrasi praktik", "value": "D", "scores": {"tanah": 5, "extrovert": 3, "praktis": 5, "kinestetik": 5}}
                ],
                "order": 7,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Apa yang paling memotivasi Anda dalam bekerja?",
                "question": "Apa yang paling memotivasi Anda dalam bekerja?",
                "category": "interest",
                "options": [
                    {"text": "Pencapaian dan pengakuan", "value": "A", "scores": {"api": 5, "extrovert": 4, "enterprising": 5, "komunikasi": 3}},
                    {"text": "Pembelajaran dan pertumbuhan", "value": "B", "scores": {"air": 5, "introvert": 4, "investigatif": 5, "logika": 4}},
                    {"text": "Stabilitas dan keamanan", "value": "C", "scores": {"tanah": 5, "introvert": 3, "praktis": 5, "logika": 3}},
                    {"text": "Dampak positif pada orang lain", "value": "D", "scores": {"kayu": 4, "extrovert": 3, "sosial": 5, "empati": 5}}
                ],
                "order": 8,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Bagaimana Anda menghadapi perubahan?",
                "question": "Bagaimana Anda menghadapi perubahan?",
                "category": "personality",
                "options": [
                    {"text": "Dengan antusias dan cepat beradaptasi", "value": "A", "scores": {"kayu": 5, "extrovert": 4, "artistik": 4, "enterprising": 4}},
                    {"text": "Dengan hati-hati setelah pertimbangan matang", "value": "B", "scores": {"logam": 5, "introvert": 4, "analitik": 5, "logika": 5}},
                    {"text": "Dengan mencari dukungan dari orang lain", "value": "C", "scores": {"api": 4, "extrovert": 4, "sosial": 5, "empati": 4}},
                    {"text": "Dengan fokus pada hal yang bisa dikontrol", "value": "D", "scores": {"tanah": 5, "introvert": 3, "praktis": 5, "logika": 4}}
                ],
                "order": 9,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Lingkungan kerja ideal untuk saya adalah:",
                "question": "Lingkungan kerja ideal untuk saya adalah:",
                "category": "interest",
                "options": [
                    {"text": "Dinamis dengan banyak tantangan", "value": "A", "scores": {"api": 5, "extrovert": 4, "enterprising": 5, "kinestetik": 3}},
                    {"text": "Terstruktur dan terorganisir", "value": "B", "scores": {"logam": 5, "introvert": 4, "analitik": 4, "logika": 5}},
                    {"text": "Kolaboratif dan suportif", "value": "C", "scores": {"tanah": 4, "extrovert": 4, "sosial": 5, "empati": 4}},
                    {"text": "Fleksibel dan mandiri", "value": "D", "scores": {"kayu": 5, "introvert": 5, "artistik": 4, "investigatif": 4}}
                ],
                "order": 10,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Kekuatan utama saya adalah:",
                "question": "Kekuatan utama saya adalah:",
                "category": "talent",
                "options": [
                    {"text": "Berpikir analitis dan kritis", "value": "A", "scores": {"logam": 5, "introvert": 4, "analitik": 5, "logika": 5}},
                    {"text": "Kreativitas dan inovasi", "value": "B", "scores": {"kayu": 5, "introvert": 3, "artistik": 5, "visual": 5}},
                    {"text": "Empati dan komunikasi", "value": "C", "scores": {"api": 5, "extrovert": 4, "sosial": 5, "empati": 5}},
                    {"text": "Organisasi dan eksekusi", "value": "D", "scores": {"tanah": 5, "extrovert": 2, "praktis": 5, "logika": 4}}
                ],
                "order": 11,
                "isFree": False,
                "isActive": True,
                "weight": 1.3,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Ketika belajar hal baru, saya lebih suka:",
                "question": "Ketika belajar hal baru, saya lebih suka:",
                "category": "skills",
                "options": [
                    {"text": "Membaca dan meneliti sendiri", "value": "A", "scores": {"air": 5, "introvert": 5, "investigatif": 5, "logika": 4}},
                    {"text": "Menonton video atau tutorial visual", "value": "B", "scores": {"kayu": 4, "introvert": 3, "visual": 5, "artistik": 4}},
                    {"text": "Diskusi dan belajar bersama", "value": "C", "scores": {"api": 4, "extrovert": 5, "sosial": 5, "komunikasi": 4}},
                    {"text": "Langsung praktik dan coba-coba", "value": "D", "scores": {"tanah": 5, "extrovert": 3, "praktis": 5, "kinestetik": 5}}
                ],
                "order": 12,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Apa yang membuat Anda merasa paling puas?",
                "question": "Apa yang membuat Anda merasa paling puas?",
                "category": "interest",
                "options": [
                    {"text": "Menyelesaikan proyek yang menantang", "value": "A", "scores": {"logam": 5, "introvert": 3, "analitik": 4, "enterprising": 4}},
                    {"text": "Menciptakan sesuatu yang unik", "value": "B", "scores": {"kayu": 5, "introvert": 4, "artistik": 5, "visual": 5}},
                    {"text": "Membantu orang lain sukses", "value": "C", "scores": {"api": 4, "extrovert": 4, "sosial": 5, "empati": 5}},
                    {"text": "Mencapai target yang ditetapkan", "value": "D", "scores": {"tanah": 5, "extrovert": 2, "praktis": 5, "logika": 4}}
                ],
                "order": 13,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Bagaimana Anda menangani konflik?",
                "question": "Bagaimana Anda menangani konflik?",
                "category": "personality",
                "options": [
                    {"text": "Menghadapi langsung dengan tegas", "value": "A", "scores": {"api": 5, "extrovert": 5, "enterprising": 4, "komunikasi": 4}},
                    {"text": "Mencari kompromi yang adil", "value": "B", "scores": {"logam": 4, "extrovert": 2, "analitik": 4, "empati": 4}},
                    {"text": "Menghindari dan memberi waktu", "value": "C", "scores": {"air": 5, "introvert": 5, "investigatif": 3, "empati": 3}},
                    {"text": "Mencari mediator atau bantuan", "value": "D", "scores": {"tanah": 4, "extrovert": 3, "sosial": 4, "praktis": 4}}
                ],
                "order": 14,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Apa tujuan karir jangka panjang Anda?",
                "question": "Apa tujuan karir jangka panjang Anda?",
                "category": "interest",
                "options": [
                    {"text": "Menjadi ahli di bidang tertentu", "value": "A", "scores": {"air": 5, "introvert": 4, "investigatif": 5, "analitik": 5}},
                    {"text": "Memimpin tim atau organisasi", "value": "B", "scores": {"api": 5, "extrovert": 5, "enterprising": 5, "komunikasi": 4}},
                    {"text": "Memiliki bisnis sendiri", "value": "C", "scores": {"kayu": 5, "extrovert": 3, "enterprising": 5, "praktis": 4}},
                    {"text": "Memberikan kontribusi sosial", "value": "D", "scores": {"tanah": 4, "extrovert": 3, "sosial": 5, "empati": 5}}
                ],
                "order": 15,
                "isFree": False,
                "isActive": True,
                "weight": 1.3,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Bagaimana Anda merespons ketika seseorang mengkritik pekerjaan Anda?",
                "question": "Bagaimana Anda merespons ketika seseorang mengkritik pekerjaan Anda?",
                "category": "personality",
                "options": [
                    {"text": "Menerima dengan terbuka dan memperbaiki", "value": "A", "scores": {"air": 5, "introvert": 3, "analitik": 4, "empati": 4}},
                    {"text": "Mempertahankan pendapat dengan argumen", "value": "B", "scores": {"api": 5, "extrovert": 4, "komunikasi": 5, "logika": 4}},
                    {"text": "Merasa tersinggung tapi diam", "value": "C", "scores": {"kayu": 3, "introvert": 5, "artistik": 3, "empati": 3}},
                    {"text": "Meminta penjelasan lebih detail", "value": "D", "scores": {"logam": 5, "introvert": 3, "analitik": 5, "investigatif": 4}}
                ],
                "order": 16,
                "isFree": False,
                "isActive": True,
                "weight": 1.0,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Ketika Anda memiliki waktu luang, Anda lebih memilih untuk:",
                "question": "Ketika Anda memiliki waktu luang, Anda lebih memilih untuk:",
                "category": "interest",
                "options": [
                    {"text": "Membaca buku atau menonton film", "value": "A", "scores": {"air": 5, "introvert": 5, "investigatif": 4, "visual": 4}},
                    {"text": "Berkumpul dengan teman-teman", "value": "B", "scores": {"api": 5, "extrovert": 5, "sosial": 5, "komunikasi": 4}},
                    {"text": "Melakukan hobi kreatif", "value": "C", "scores": {"kayu": 5, "introvert": 4, "artistik": 5, "visual": 5}},
                    {"text": "Beristirahat dan me-time", "value": "D", "scores": {"tanah": 4, "introvert": 5, "praktis": 3, "empati": 3}}
                ],
                "order": 17,
                "isFree": False,
                "isActive": True,
                "weight": 1.0,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Bagaimana cara Anda mengatur prioritas tugas?",
                "question": "Bagaimana cara Anda mengatur prioritas tugas?",
                "category": "skills",
                "options": [
                    {"text": "Membuat daftar dan mengerjakan dari yang terpenting", "value": "A", "scores": {"logam": 5, "introvert": 4, "analitik": 5, "logika": 5}},
                    {"text": "Mengerjakan yang paling mudah terlebih dahulu", "value": "B", "scores": {"tanah": 4, "extrovert": 2, "praktis": 4, "kinestetik": 3}},
                    {"text": "Multitasking semua sekaligus", "value": "C", "scores": {"api": 4, "extrovert": 4, "enterprising": 3, "kinestetik": 4}},
                    {"text": "Mengikuti deadline yang paling dekat", "value": "D", "scores": {"kayu": 3, "extrovert": 2, "praktis": 4, "logika": 3}}
                ],
                "order": 18,
                "isFree": False,
                "isActive": True,
                "weight": 1.0,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Apa yang membuat Anda merasa termotivasi untuk bangun pagi?",
                "question": "Apa yang membuat Anda merasa termotivasi untuk bangun pagi?",
                "category": "interest",
                "options": [
                    {"text": "Tujuan dan target yang ingin dicapai", "value": "A", "scores": {"api": 5, "extrovert": 3, "enterprising": 5, "logika": 4}},
                    {"text": "Tanggung jawab terhadap keluarga atau pekerjaan", "value": "B", "scores": {"tanah": 5, "extrovert": 2, "sosial": 4, "empati": 4}},
                    {"text": "Kebiasaan yang sudah terbentuk", "value": "C", "scores": {"logam": 4, "introvert": 3, "praktis": 5, "logika": 3}},
                    {"text": "Rencana menyenangkan di hari itu", "value": "D", "scores": {"kayu": 5, "extrovert": 4, "artistik": 4, "sosial": 4}}
                ],
                "order": 19,
                "isFree": False,
                "isActive": True,
                "weight": 1.0,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Apa nilai yang paling Anda junjung tinggi dalam hidup?",
                "question": "Apa nilai yang paling Anda junjung tinggi dalam hidup?",
                "category": "personality",
                "options": [
                    {"text": "Kejujuran dan integritas", "value": "A", "scores": {"logam": 5, "introvert": 4, "analitik": 4, "logika": 5}},
                    {"text": "Kesetiaan dan loyalitas", "value": "B", "scores": {"tanah": 5, "introvert": 3, "sosial": 4, "empati": 5}},
                    {"text": "Kebebasan dan kemandirian", "value": "C", "scores": {"kayu": 5, "introvert": 4, "artistik": 4, "enterprising": 4}},
                    {"text": "Keharmonisan dan kedamaian", "value": "D", "scores": {"air": 5, "introvert": 5, "empati": 5, "sosial": 3}}
                ],
                "order": 20,
                "isFree": False,
                "isActive": True,
                "weight": 1.3,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Bagaimana Anda mendeskripsikan gaya kepemimpinan Anda?",
                "question": "Bagaimana Anda mendeskripsikan gaya kepemimpinan Anda?",
                "category": "talent",
                "options": [
                    {"text": "Demokratis - melibatkan semua anggota", "value": "A", "scores": {"air": 4, "extrovert": 3, "sosial": 5, "empati": 5}},
                    {"text": "Visioner - memberi arahan jelas", "value": "B", "scores": {"api": 5, "extrovert": 5, "enterprising": 5, "komunikasi": 5}},
                    {"text": "Suportif - mendukung dari belakang", "value": "C", "scores": {"tanah": 5, "introvert": 3, "empati": 5, "praktis": 4}},
                    {"text": "Delegatif - mempercayakan kepada tim", "value": "D", "scores": {"logam": 5, "introvert": 4, "analitik": 4, "logika": 5}}
                ],
                "order": 21,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Bagaimana Anda menangani kegagalan?",
                "question": "Bagaimana Anda menangani kegagalan?",
                "category": "personality",
                "options": [
                    {"text": "Belajar dari kesalahan dan mencoba lagi", "value": "A", "scores": {"kayu": 5, "extrovert": 3, "enterprising": 5, "praktis": 4}},
                    {"text": "Menganalisis apa yang salah", "value": "B", "scores": {"logam": 5, "introvert": 4, "analitik": 5, "logika": 5}},
                    {"text": "Merasa kecewa tapi bangkit kembali", "value": "C", "scores": {"api": 4, "extrovert": 3, "empati": 4, "sosial": 3}},
                    {"text": "Menghindari situasi serupa di masa depan", "value": "D", "scores": {"air": 4, "introvert": 5, "investigatif": 3, "praktis": 3}}
                ],
                "order": 22,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Bagaimana cara Anda mengekspresikan kreativitas?",
                "question": "Bagaimana cara Anda mengekspresikan kreativitas?",
                "category": "talent",
                "options": [
                    {"text": "Melalui seni visual atau musik", "value": "A", "scores": {"kayu": 5, "introvert": 4, "artistik": 5, "visual": 5, "musikal": 5}},
                    {"text": "Melalui tulisan atau cerita", "value": "B", "scores": {"air": 5, "introvert": 5, "artistik": 4, "komunikasi": 4}},
                    {"text": "Melalui pemecahan masalah inovatif", "value": "C", "scores": {"logam": 5, "introvert": 3, "analitik": 5, "logika": 5}},
                    {"text": "Melalui fashion atau desain interior", "value": "D", "scores": {"tanah": 4, "extrovert": 3, "visual": 5, "praktis": 4}}
                ],
                "order": 23,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Apa yang Anda utamakan dalam pekerjaan?",
                "question": "Apa yang Anda utamakan dalam pekerjaan?",
                "category": "interest",
                "options": [
                    {"text": "Passion dan kepuasan batin", "value": "A", "scores": {"kayu": 5, "introvert": 4, "artistik": 5, "empati": 4}},
                    {"text": "Stabilitas dan keamanan finansial", "value": "B", "scores": {"tanah": 5, "introvert": 3, "praktis": 5, "logika": 4}},
                    {"text": "Peluang berkembang", "value": "C", "scores": {"api": 5, "extrovert": 4, "enterprising": 5, "investigatif": 4}},
                    {"text": "Work-life balance", "value": "D", "scores": {"air": 5, "introvert": 4, "empati": 4, "sosial": 3}}
                ],
                "order": 24,
                "isFree": False,
                "isActive": True,
                "weight": 1.2,
                "createdAt": datetime.utcnow()
            },
            {
                "text": "Bagaimana filosofi hidup yang Anda pegang?",
                "question": "Bagaimana filosofi hidup yang Anda pegang?",
                "category": "personality",
                "options": [
                    {"text": "Kerja keras pasti berbuah hasil", "value": "A", "scores": {"tanah": 5, "extrovert": 2, "praktis": 5, "enterprising": 4}},
                    {"text": "Hidup adalah perjalanan belajar", "value": "B", "scores": {"air": 5, "introvert": 5, "investigatif": 5, "analitik": 4}},
                    {"text": "Kebahagiaan adalah pilihan", "value": "C", "scores": {"api": 5, "extrovert": 4, "sosial": 4, "empati": 5}},
                    {"text": "Setiap hal terjadi dengan alasan", "value": "D", "scores": {"kayu": 5, "introvert": 4, "artistik": 4, "empati": 4}}
                ],
                "order": 25,
                "isFree": False,
                "isActive": True,
                "weight": 1.3,
                "createdAt": datetime.utcnow()
            }
        ]
        
        # Insert all questions
        all_questions = free_questions + paid_questions
        await db.questions.insert_many(all_questions)
        
        return {
            "message": "Questions seeded successfully dengan scoring 5 elemen",
            "free_count": len(free_questions),
            "paid_count": len(paid_questions),
            "total": len(all_questions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/clear-all")
async def clear_all_questions(token_data: dict = Depends(verify_token)):
    """Clear all questions (admin only) - for re-seeding"""
    try:
        result = await db.questions.delete_many({})
        return {"message": f"Deleted {result.deleted_count} questions"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
