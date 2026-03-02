from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from database import get_db
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from pydantic import BaseModel, EmailStr
import bcrypt
import jwt
import os
import uuid

router = APIRouter(prefix="/api/yayasan", tags=["yayasan"])
db = get_db()

JWT_SECRET = os.environ.get("JWT_SECRET_KEY", "default_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7

# Pydantic Models
class YayasanCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    address: Optional[str] = None
    description: Optional[str] = None

class YayasanLogin(BaseModel):
    email: EmailStr
    password: str

class YayasanReferralPriceUpdate(BaseModel):
    referralPrice: float
    discountPercentage: Optional[float] = 0

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_yayasan_token(yayasan_id: str, email: str) -> str:
    payload = {
        "sub": yayasan_id,
        "email": email,
        "type": "yayasan",
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_yayasan_referral_code(name: str) -> str:
    """Generate unique referral code for yayasan"""
    prefix = "YYS"
    name_part = ''.join(c for c in name[:3].upper() if c.isalnum())
    suffix = uuid.uuid4().hex[:4].upper()
    return f"{prefix}{name_part}{suffix}"

async def get_current_yayasan(request: Request):
    """Dependency to get current authenticated yayasan"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token tidak valid")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "yayasan":
            raise HTTPException(status_code=403, detail="Bukan akun yayasan")
        yayasan = await db.yayasan.find_one({"_id": ObjectId(payload["sub"])})
        if not yayasan:
            raise HTTPException(status_code=401, detail="Yayasan tidak ditemukan")
        if not yayasan.get("isActive", True):
            raise HTTPException(status_code=403, detail="Akun yayasan dinonaktifkan")
        return yayasan
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token sudah expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token tidak valid: {str(e)}")

@router.post("/register", response_model=dict)
async def register_yayasan(data: YayasanCreate, request: Request):
    """Register new yayasan/foundation"""
    try:
        # Check if email exists
        existing = await db.yayasan.find_one({"email": data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar")
        
        # Hash password
        hashed_password = hash_password(data.password)
        
        # Generate referral code
        referral_code = generate_yayasan_referral_code(data.name)
        
        # Get default test price from settings
        settings = await db.settings.find_one()
        default_price = settings.get("paymentAmount", 100000) if settings else 100000
        
        yayasan_doc = {
            "name": data.name,
            "email": data.email,
            "hashedPassword": hashed_password,
            "phone": data.phone,
            "address": data.address,
            "description": data.description,
            "referralCode": referral_code,
            "referralPrice": default_price,  # Price for users using this referral
            "discountPercentage": 0,
            "isActive": True,
            "isVerified": False,
            "totalReferrals": 0,
            "totalEarnings": 0,
            "createdAt": datetime.utcnow(),
            "ipAddress": request.client.host
        }
        
        result = await db.yayasan.insert_one(yayasan_doc)
        yayasan_id = str(result.inserted_id)
        
        token = create_yayasan_token(yayasan_id, data.email)
        
        return {
            "success": True,
            "token": token,
            "yayasan": {
                "id": yayasan_id,
                "name": data.name,
                "email": data.email,
                "referralCode": referral_code,
                "referralPrice": default_price
            },
            "message": "Pendaftaran yayasan berhasil!"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/login", response_model=dict)
async def login_yayasan(credentials: YayasanLogin, request: Request):
    """Login yayasan"""
    try:
        yayasan = await db.yayasan.find_one({"email": credentials.email})
        if not yayasan:
            raise HTTPException(status_code=401, detail="Email atau password salah")
        
        if not verify_password(credentials.password, yayasan["hashedPassword"]):
            raise HTTPException(status_code=401, detail="Email atau password salah")
        
        if not yayasan.get("isActive", True):
            raise HTTPException(status_code=403, detail="Akun yayasan dinonaktifkan")
        
        # Update last login
        await db.yayasan.update_one(
            {"_id": yayasan["_id"]},
            {"$set": {"lastLoginAt": datetime.utcnow(), "ipAddress": request.client.host}}
        )
        
        yayasan_id = str(yayasan["_id"])
        token = create_yayasan_token(yayasan_id, yayasan["email"])
        
        return {
            "success": True,
            "token": token,
            "yayasan": {
                "id": yayasan_id,
                "name": yayasan["name"],
                "email": yayasan["email"],
                "referralCode": yayasan["referralCode"],
                "referralPrice": yayasan.get("referralPrice", 100000),
                "discountPercentage": yayasan.get("discountPercentage", 0),
                "totalReferrals": yayasan.get("totalReferrals", 0),
                "totalEarnings": yayasan.get("totalEarnings", 0),
                "isVerified": yayasan.get("isVerified", False)
            },
            "message": "Login berhasil"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/me", response_model=dict)
async def get_yayasan_profile(current_yayasan: dict = Depends(get_current_yayasan)):
    """Get current yayasan profile"""
    return {
        "id": str(current_yayasan["_id"]),
        "name": current_yayasan["name"],
        "email": current_yayasan["email"],
        "phone": current_yayasan.get("phone"),
        "address": current_yayasan.get("address"),
        "description": current_yayasan.get("description"),
        "referralCode": current_yayasan["referralCode"],
        "referralPrice": current_yayasan.get("referralPrice", 100000),
        "discountPercentage": current_yayasan.get("discountPercentage", 0),
        "totalReferrals": current_yayasan.get("totalReferrals", 0),
        "totalEarnings": current_yayasan.get("totalEarnings", 0),
        "isActive": current_yayasan.get("isActive", True),
        "isVerified": current_yayasan.get("isVerified", False),
        "createdAt": current_yayasan.get("createdAt")
    }

@router.put("/referral-price", response_model=dict)
async def update_referral_price(
    data: YayasanReferralPriceUpdate,
    current_yayasan: dict = Depends(get_current_yayasan)
):
    """Update referral price for yayasan's referral link"""
    try:
        # Get min/max price limits from settings
        settings = await db.settings.find_one()
        min_price = settings.get("minReferralPrice", 25000) if settings else 25000
        max_price = settings.get("paymentAmount", 100000) if settings else 100000
        
        if data.referralPrice < min_price:
            raise HTTPException(
                status_code=400, 
                detail=f"Harga minimal adalah Rp {min_price:,}"
            )
        
        if data.referralPrice > max_price:
            raise HTTPException(
                status_code=400, 
                detail=f"Harga maksimal adalah Rp {max_price:,}"
            )
        
        await db.yayasan.update_one(
            {"_id": current_yayasan["_id"]},
            {"$set": {
                "referralPrice": data.referralPrice,
                "discountPercentage": data.discountPercentage or 0,
                "updatedAt": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "Harga referral berhasil diupdate",
            "referralPrice": data.referralPrice,
            "discountPercentage": data.discountPercentage or 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/dashboard/stats", response_model=dict)
async def get_yayasan_dashboard_stats(current_yayasan: dict = Depends(get_current_yayasan)):
    """Get dashboard statistics for yayasan"""
    try:
        # Get users who used this yayasan's referral code
        referral_code = current_yayasan["referralCode"]
        
        # Get users who used this yayasan's referral code
        total_users = await db.users.count_documents({"usedReferralCode": referral_code})
        
        # Get users with completed paid tests
        completed_tests = await db.users.count_documents({
            "usedReferralCode": referral_code,
            "paidTestStatus": "completed"
        })
        
        # Get pending payments
        pending_users = await db.users.count_documents({
            "usedReferralCode": referral_code,
            "paymentStatus": "pending"
        })
        
        # Get paid users
        paid_users = await db.users.count_documents({
            "usedReferralCode": referral_code,
            "paymentStatus": "approved"
        })
        
        # Get recent users
        recent_users = await db.users.find(
            {"usedReferralCode": referral_code},
            {"fullName": 1, "email": 1, "paymentStatus": 1, "paidTestStatus": 1, "createdAt": 1}
        ).sort("createdAt", -1).limit(10).to_list(10)
        
        for user in recent_users:
            user["_id"] = str(user["_id"])
        
        # Calculate earnings
        referral_price = current_yayasan.get("referralPrice", 100000)
        total_earnings = paid_users * (referral_price * 0.1)  # 10% commission
        
        return {
            "totalUsers": total_users,
            "completedTests": completed_tests,
            "pendingUsers": pending_users,
            "paidUsers": paid_users,
            "totalEarnings": total_earnings,
            "referralCode": referral_code,
            "referralPrice": referral_price,
            "recentUsers": recent_users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/users", response_model=List[dict])
async def get_yayasan_users(
    current_yayasan: dict = Depends(get_current_yayasan),
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None
):
    """Get users who registered using yayasan's referral code"""
    try:
        referral_code = current_yayasan["referralCode"]
        
        query = {"usedReferralCode": referral_code}
        if status:
            if status == "paid":
                query["paymentStatus"] = "approved"
            elif status == "pending":
                query["paymentStatus"] = "pending"
            elif status == "completed":
                query["paidTestStatus"] = "completed"
        
        users = await db.users.find(
            query,
            {
                "fullName": 1, "email": 1, "whatsapp": 1, 
                "paymentStatus": 1, "paidTestStatus": 1, "freeTestStatus": 1,
                "createdAt": 1, "province": 1, "city": 1
            }
        ).skip(skip).limit(limit).sort("createdAt", -1).to_list(limit)
        
        for user in users:
            user["_id"] = str(user["_id"])
        
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/test-results", response_model=List[dict])
async def get_yayasan_test_results(
    current_yayasan: dict = Depends(get_current_yayasan),
    skip: int = 0,
    limit: int = 50
):
    """Get premium test results of users who used this yayasan's referral code"""
    try:
        referral_code = current_yayasan["referralCode"]
        # Find users with this referral code
        referral_users = await db.users.find(
            {"usedReferralCode": referral_code},
            {"_id": 1, "fullName": 1, "email": 1}
        ).to_list(500)
        user_ids = [str(u["_id"]) for u in referral_users]
        user_map = {str(u["_id"]): u for u in referral_users}

        if not user_ids:
            return []

        results = await db.test_results.find(
            {"userId": {"$in": user_ids}, "testType": "paid"}
        ).sort("createdAt", -1).skip(skip).limit(limit).to_list(limit)

        for r in results:
            r["_id"] = str(r["_id"])
            user = user_map.get(r.get("userId"), {})
            r["userName"] = user.get("fullName", "")
            r["userEmail"] = user.get("email", "")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/wallet", response_model=dict)
async def get_yayasan_wallet(current_yayasan: dict = Depends(get_current_yayasan)):
    """Get yayasan wallet balance and transactions"""
    try:
        yayasan_id = str(current_yayasan["_id"])
        wallet = await db.yayasan_wallets.find_one({"yayasanId": yayasan_id}) or {"balance": 0}
        txns = await db.yayasan_transactions.find(
            {"yayasanId": yayasan_id}
        ).sort("createdAt", -1).limit(20).to_list(20)
        for t in txns:
            t["_id"] = str(t["_id"])
        return {
            "balance": wallet.get("balance", 0),
            "transactions": txns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/wallet/withdraw", response_model=dict)
async def request_yayasan_withdrawal(
    request: dict,
    current_yayasan: dict = Depends(get_current_yayasan)
):
    """Request withdrawal from yayasan wallet"""
    try:
        amount = request.get("amount", 0)
        bank_name = request.get("bankName", "")
        bank_account = request.get("bankAccount", "")
        account_name = request.get("accountName", "")

        if amount < 50000:
            raise HTTPException(status_code=400, detail="Minimal penarikan Rp 50.000")

        yayasan_id = str(current_yayasan["_id"])
        wallet = await db.yayasan_wallets.find_one({"yayasanId": yayasan_id})
        balance = wallet.get("balance", 0) if wallet else 0

        if balance < amount:
            raise HTTPException(status_code=400, detail="Saldo tidak mencukupi")

        # Deduct balance and create withdrawal request
        await db.yayasan_wallets.update_one(
            {"yayasanId": yayasan_id},
            {"$inc": {"balance": -amount}},
            upsert=True
        )
        await db.yayasan_transactions.insert_one({
            "yayasanId": yayasan_id,
            "type": "withdrawal",
            "amount": amount,
            "bankName": bank_name,
            "bankAccount": bank_account,
            "accountName": account_name,
            "status": "pending",
            "createdAt": datetime.utcnow()
        })
        return {"success": True, "message": "Permintaan penarikan berhasil diajukan"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



async def check_yayasan_referral(code: str):
    """Check if a referral code belongs to a yayasan and get the price"""
    try:
        yayasan = await db.yayasan.find_one({"referralCode": code, "isActive": True})
        
        if not yayasan:
            return {
                "isYayasan": False,
                "message": "Kode referral tidak ditemukan atau bukan dari yayasan"
            }
        
        return {
            "isYayasan": True,
            "yayasanName": yayasan["name"],
            "referralPrice": yayasan.get("referralPrice", 100000),
            "discountPercentage": yayasan.get("discountPercentage", 0),
            "message": f"Kode referral dari {yayasan['name']}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Admin endpoints for managing yayasan
@router.get("/admin/list", response_model=List[dict])
async def admin_get_all_yayasan(
    skip: int = 0,
    limit: int = 50
):
    """Get all yayasan (admin only)"""
    try:
        yayasan_list = await db.yayasan.find(
            {},
            {"hashedPassword": 0}
        ).skip(skip).limit(limit).sort("createdAt", -1).to_list(limit)
        
        for y in yayasan_list:
            y["_id"] = str(y["_id"])
        
        return yayasan_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/admin/{yayasan_id}/toggle-active", response_model=dict)
async def admin_toggle_yayasan_active(yayasan_id: str):
    """Toggle yayasan active status (admin only)"""
    try:
        yayasan = await db.yayasan.find_one({"_id": ObjectId(yayasan_id)})
        if not yayasan:
            raise HTTPException(status_code=404, detail="Yayasan tidak ditemukan")
        
        new_status = not yayasan.get("isActive", True)
        
        await db.yayasan.update_one(
            {"_id": ObjectId(yayasan_id)},
            {"$set": {"isActive": new_status, "updatedAt": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "message": f"Yayasan {'diaktifkan' if new_status else 'dinonaktifkan'}",
            "isActive": new_status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/admin/{yayasan_id}/verify", response_model=dict)
async def admin_verify_yayasan(yayasan_id: str):
    """Verify yayasan (admin only)"""
    try:
        result = await db.yayasan.update_one(
            {"_id": ObjectId(yayasan_id)},
            {"$set": {"isVerified": True, "verifiedAt": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Yayasan tidak ditemukan")
        
        return {
            "success": True,
            "message": "Yayasan berhasil diverifikasi"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



# Admin endpoints for managing withdrawals
@router.get("/admin/withdrawals", response_model=List[dict])
async def admin_get_withdrawals(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all yayasan withdrawal requests (admin only)"""
    try:
        query = {"type": "withdrawal"}
        if status:
            query["status"] = status
        
        withdrawals = await db.yayasan_transactions.find(query).sort("createdAt", -1).skip(skip).limit(limit).to_list(limit)
        
        # Enrich with yayasan info
        for w in withdrawals:
            w["_id"] = str(w["_id"])
            yayasan = await db.yayasan.find_one({"_id": ObjectId(w["yayasanId"])})
            if yayasan:
                w["yayasanName"] = yayasan.get("name", "")
                w["yayasanEmail"] = yayasan.get("email", "")
        
        return withdrawals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.put("/admin/withdrawals/{withdrawal_id}/approve", response_model=dict)
async def admin_approve_withdrawal(withdrawal_id: str, action: dict):
    """Approve or reject yayasan withdrawal (admin only)"""
    try:
        status = action.get("status", "approved")
        notes = action.get("notes", "")
        
        withdrawal = await db.yayasan_transactions.find_one({"_id": ObjectId(withdrawal_id)})
        if not withdrawal:
            raise HTTPException(status_code=404, detail="Penarikan tidak ditemukan")
        
        if withdrawal.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Penarikan sudah diproses")
        
        update_data = {
            "status": status,
            "processedAt": datetime.utcnow(),
            "adminNotes": notes
        }
        
        await db.yayasan_transactions.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {"$set": update_data}
        )
        
        # If rejected, refund the balance
        if status == "rejected":
            await db.yayasan_wallets.update_one(
                {"yayasanId": withdrawal["yayasanId"]},
                {"$inc": {"balance": withdrawal["amount"]}}
            )
        
        return {
            "success": True,
            "message": f"Penarikan berhasil {'disetujui' if status == 'approved' else 'ditolak'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
