from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import List, Optional
from models.payment import Payment, PaymentApproval
from database import get_db
from datetime import datetime
from bson import ObjectId
import os
import uuid
from pathlib import Path
from routes.admin import verify_token

router = APIRouter(prefix="/api/payments", tags=["payments"])
db = get_db()

# Upload directory
UPLOAD_DIR = Path("/app/frontend/public/uploads/payments")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload-proof")
async def upload_payment_proof(
    registrationId: str = Form(...),
    paymentAmount: float = Form(...),
    paymentMethod: str = Form(...),
    notes: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """
    Upload payment proof for registration
    """
    try:
        # Validate file type
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="File type not allowed. Only PNG, JPG, and JPEG are accepted."
            )
        
        # Get registration details
        if not ObjectId.is_valid(registrationId):
            raise HTTPException(status_code=400, detail="Invalid registration ID")
        
        registration = await db.registrations.find_one({"_id": ObjectId(registrationId)})
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        # Check if payment already exists
        existing_payment = await db.payments.find_one({"registrationId": registrationId})
        if existing_payment and existing_payment.get("status") == "approved":
            raise HTTPException(status_code=400, detail="Payment already approved for this registration")
        
        # Save file
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Create payment record
        payment_data = {
            "registrationId": registrationId,
            "userId": str(registration["_id"]),
            "userName": registration["name"],
            "userEmail": registration["email"],
            "paymentAmount": paymentAmount,
            "paymentMethod": paymentMethod,
            "paymentProofUrl": f"/uploads/payments/{unique_filename}",
            "status": "pending",
            "uploadedAt": datetime.utcnow(),
            "notes": notes
        }
        
        # Update existing or create new
        if existing_payment:
            await db.payments.update_one(
                {"_id": existing_payment["_id"]},
                {"$set": payment_data}
            )
            payment_id = str(existing_payment["_id"])
        else:
            result = await db.payments.insert_one(payment_data)
            payment_id = str(result.inserted_id)
        
        return {
            "success": True,
            "paymentId": payment_id,
            "message": "Bukti pembayaran berhasil diupload. Menunggu approval admin."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("", response_model=List[dict])
async def get_payments(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    token_data: dict = Depends(verify_token)
):
    """
    Get all payments (admin only)
    """
    try:
        query = {}
        if status:
            query["status"] = status
        
        # Check both payment_proofs and payments collections
        cursor1 = db.payment_proofs.find(query).skip(skip).limit(limit).sort("createdAt", -1)
        payments1 = await cursor1.to_list(length=limit)
        
        cursor2 = db.payments.find(query).skip(skip).limit(limit).sort("uploadedAt", -1)
        payments2 = await cursor2.to_list(length=limit)
        
        # Combine and normalize data
        all_payments = []
        
        # Process payment_proofs
        for payment in payments1:
            all_payments.append({
                "_id": str(payment["_id"]),
                "userId": payment.get("userId"),
                "userName": payment.get("userName"),
                "userEmail": payment.get("userEmail"),
                "paymentAmount": payment.get("grossAmount", 0),
                "paymentMethod": payment.get("paymentMethod", ""),
                "paymentProofUrl": payment.get("proofUrl", ""),
                "status": payment.get("status", "pending"),
                "uploadedAt": payment.get("createdAt"),
                "notes": payment.get("notes", ""),
                "orderId": payment.get("orderId", "")
            })
        
        # Process payments
        for payment in payments2:
            all_payments.append({
                "_id": str(payment["_id"]),
                "userId": payment.get("userId"),
                "userName": payment.get("userName"),
                "userEmail": payment.get("userEmail"),
                "paymentAmount": payment.get("paymentAmount", 0),
                "paymentMethod": payment.get("paymentMethod", ""),
                "paymentProofUrl": payment.get("paymentProofUrl", ""),
                "status": payment.get("status", "pending"),
                "uploadedAt": payment.get("uploadedAt"),
                "notes": payment.get("notes", ""),
                "registrationId": payment.get("registrationId", "")
            })
        
        # Sort by date
        all_payments.sort(key=lambda x: x.get("uploadedAt", ""), reverse=True)
        
        return all_payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/{payment_id}/approve", response_model=dict)
async def approve_payment(
    payment_id: str,
    approval: PaymentApproval,
    token_data: dict = Depends(verify_token)
):
    """
    Approve or reject payment
    """
    try:
        if not ObjectId.is_valid(payment_id):
            raise HTTPException(status_code=400, detail="Invalid payment ID")
        
        # Check in payment_proofs first
        payment = await db.payment_proofs.find_one({"_id": ObjectId(payment_id)})
        collection = "payment_proofs"
        
        # If not found, check in payments collection
        if not payment:
            payment = await db.payments.find_one({"_id": ObjectId(payment_id)})
            collection = "payments"
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        update_data = {
            "status": approval.status,
            "approvedAt": datetime.utcnow(),
            "approvedBy": token_data["sub"]
        }
        
        if approval.status == "rejected" and approval.rejectionReason:
            update_data["rejectionReason"] = approval.rejectionReason
        
        if approval.notes:
            update_data["notes"] = approval.notes
        
        # Update payment in correct collection
        if collection == "payment_proofs":
            await db.payment_proofs.update_one(
                {"_id": ObjectId(payment_id)},
                {"$set": update_data}
            )
            
            # Update user status if approved
            if approval.status == "approved" and payment.get("userId"):
                await db.users.update_one(
                    {"_id": ObjectId(payment["userId"])},
                    {"$set": {
                        "paymentStatus": "approved",
                        "paidTestStatus": "in_progress",
                        "paymentDate": datetime.utcnow()
                    }}
                )
                
                # Credit yayasan commission if payment has referral code
                referral_code = payment.get("referralCode")
                if referral_code:
                    await credit_yayasan_commission(
                        referral_code=referral_code,
                        payment_amount=payment.get("grossAmount", 0),
                        user_id=payment.get("userId"),
                        payment_id=payment_id
                    )
        else:
            await db.payments.update_one(
                {"_id": ObjectId(payment_id)},
                {"$set": update_data}
            )
            
            # Update registration status if approved
            if approval.status == "approved" and payment.get("registrationId"):
                await db.registrations.update_one(
                    {"_id": ObjectId(payment["registrationId"])},
                    {"$set": {
                        "testStatus": "approved",
                        "isMember": True
                    }}
                )
        
        return {
            "success": True,
            "message": f"Payment {approval.status} successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/registration/{registration_id}", response_model=dict)
async def get_payment_by_registration(registration_id: str):
    """
    Get payment by registration ID
    """
    try:
        payment = await db.payments.find_one({"registrationId": registration_id})
        if payment:
            payment["_id"] = str(payment["_id"])
            return payment
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/stats/summary", response_model=dict)
async def get_payment_stats(token_data: dict = Depends(verify_token)):
    """
    Get payment statistics
    """
    try:
        total = await db.payments.count_documents({})
        pending = await db.payments.count_documents({"status": "pending"})
        approved = await db.payments.count_documents({"status": "approved"})
        rejected = await db.payments.count_documents({"status": "rejected"})
        
        # Calculate total revenue
        pipeline = [
            {"$match": {"status": "approved"}},
            {"$group": {"_id": None, "totalRevenue": {"$sum": "$paymentAmount"}}}
        ]
        revenue_result = await db.payments.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]["totalRevenue"] if revenue_result else 0
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "totalRevenue": total_revenue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


async def credit_yayasan_commission(referral_code: str, payment_amount: float, user_id: str, payment_id: str):
    """Credit commission to yayasan wallet when referred user payment is approved"""
    try:
        # Find yayasan by referral code
        yayasan = await db.yayasan.find_one({"referralCode": referral_code, "isActive": True})
        if not yayasan:
            return
        
        yayasan_id = str(yayasan["_id"])
        
        # Calculate commission (10% of payment)
        commission_rate = 0.10
        commission_amount = payment_amount * commission_rate
        
        # Update or create yayasan wallet
        await db.yayasan_wallets.update_one(
            {"yayasanId": yayasan_id},
            {"$inc": {"balance": commission_amount}},
            upsert=True
        )
        
        # Record transaction
        await db.yayasan_transactions.insert_one({
            "yayasanId": yayasan_id,
            "type": "commission",
            "amount": commission_amount,
            "paymentId": payment_id,
            "referredUserId": user_id,
            "status": "completed",
            "description": f"Komisi referral ({commission_rate*100:.0f}%)",
            "createdAt": datetime.utcnow()
        })
        
        # Update yayasan total earnings
        await db.yayasan.update_one(
            {"_id": yayasan["_id"]},
            {"$inc": {"totalEarnings": commission_amount, "totalReferrals": 1}}
        )
        
    except Exception as e:
        print(f"Error crediting yayasan commission: {str(e)}")