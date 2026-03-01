from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from typing import List, Optional
from database import get_db
from datetime import datetime
from bson import ObjectId
from routes.auth import get_current_user
import uuid
import os
import logging
from pathlib import Path
import sys
sys.path.insert(0, '/app/backend')
from services import paydisini as paydisini_service

router = APIRouter(prefix="/api/user-payments", tags=["user-payments"])
db = get_db()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("/app/frontend/public/uploads/payments")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ──────────────────────────────────────────────
#  QRIS — PayDisini (service=17)
# ──────────────────────────────────────────────

@router.post("/create-qris", response_model=dict)
async def create_qris_payment(
    current_user: dict = Depends(get_current_user)
):
    """
    Buat QRIS PayDisini untuk pembayaran test premium.
    Menggunakan service=17, valid_time=300 (5 menit).
    """
    try:
        # Cek apakah ada QRIS pending dalam 10 menit terakhir
        from bson import ObjectId
        from datetime import timedelta
        ten_min_ago = datetime.utcnow() - timedelta(minutes=10)
        pending = await db.payment_proofs.find_one({
            "userId": str(current_user["_id"]),
            "paymentMethod": "QRIS",
            "status": "pending",
            "createdAt": {"$gte": ten_min_ago}
        })
        if pending:
            return {
                "success": True,
                "already_pending": True,
                "message": "Ada transaksi QRIS pending. Selesaikan pembayaran sebelumnya.",
                "data": {
                    "unique_code": pending.get("uniqueCode"),
                    "checkout_url": pending.get("checkoutUrl", ""),
                    "checkout_url_beta": pending.get("checkoutUrlBeta", ""),
                    "qr_url": pending.get("qrUrl", ""),
                    "qr_content": pending.get("qrContent", ""),
                    "amount": pending.get("grossAmount", 0)
                }
            }

        # Ambil harga dari settings
        settings = await db.settings.find_one()
        amount = int(settings.get("paymentAmount", 100000)) if settings else 100000

        # Cek apakah user menggunakan referral yayasan
        user_doc = await db.users.find_one({"_id": current_user["_id"]})
        referral_code = user_doc.get("usedReferralCode") if user_doc else None
        if referral_code:
            yayasan = await db.yayasan.find_one({"referralCode": referral_code, "isActive": True})
            if yayasan:
                amount = int(yayasan.get("referralPrice", amount))

        # Panggil PayDisini
        result = paydisini_service.create_qris(
            amount=amount,
            note=f"payment qris {amount}"
        )

        if not result.get("success"):
            msg = result.get("msg", "Gagal membuat transaksi QRIS. Silakan coba lagi.")
            raise HTTPException(status_code=502, detail=msg)

        data = result.get("data", {})
        unique_code = result.get("unique_code", "")
        checkout_url = data.get("checkout_url", "")
        checkout_url_beta = data.get("checkout_url_beta", "")
        qr_content = data.get("qr_content", "")
        qr_url = data.get("qr_url", "")
        pay_amount = data.get("amount", amount)

        # Simpan ke database
        order_id = f"QRIS-{unique_code}"
        payment_doc = {
            "userId": str(current_user["_id"]),
            "userEmail": current_user.get("email"),
            "userName": current_user.get("fullName", ""),
            "paymentType": "test",
            "paymentMethod": "QRIS",
            "grossAmount": pay_amount,
            "orderId": order_id,
            "uniqueCode": unique_code,
            "checkoutUrl": checkout_url,
            "checkoutUrlBeta": checkout_url_beta,
            "qrUrl": qr_url,
            "qrContent": qr_content,
            "status": "pending",
            "referralCode": referral_code,
            "createdAt": datetime.utcnow()
        }
        await db.payment_proofs.insert_one(payment_doc)

        return {
            "success": True,
            "message": result.get("msg", "QR Code berhasil dibuat"),
            "data": {
                "unique_code": unique_code,
                "checkout_url": checkout_url,
                "checkout_url_beta": checkout_url_beta,
                "qr_content": qr_content,
                "qr_url": qr_url,
                "amount": pay_amount
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create QRIS error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/check-qris/{unique_code}", response_model=dict)
async def check_qris_status(
    unique_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Cek status pembayaran QRIS ke PayDisini"""
    try:
        result = paydisini_service.check_payment_status(unique_code)
        logger.info(f"QRIS status check: {unique_code} → {result}")

        if result.get("success") and result.get("data", {}).get("status") == "Success":
            # Update status di database
            await db.payment_proofs.update_one(
                {"uniqueCode": unique_code},
                {"$set": {"status": "approved", "updatedAt": datetime.utcnow()}}
            )
            payment = await db.payment_proofs.find_one({"uniqueCode": unique_code})
            if payment:
                await db.users.update_one(
                    {"_id": ObjectId(payment["userId"])},
                    {"$set": {"paymentStatus": "approved", "hasPaidAccess": True, "paymentDate": datetime.utcnow()}}
                )
                if payment.get("referralCode"):
                    await credit_referral_bonus(payment["referralCode"], payment["userId"])

            return {"success": True, "status": "Success", "paid": True}

        return {
            "success": result.get("success", False),
            "status": result.get("data", {}).get("status", "Pending"),
            "paid": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


async def upload_payment_proof(
    paymentType: str = Form(...),
    paymentMethod: str = Form("bank"),
    paymentAmount: float = Form(None),
    orderId: Optional[str] = Form(None),
    referralCode: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload payment proof (manual upload, admin akan approve)
    """
    try:
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="Hanya file PNG, JPG, JPEG, GIF, WEBP yang diperbolehkan")

        # Save file
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)

        proof_url = f"/uploads/payments/{unique_filename}"

        # Get test price from settings if not provided
        if not paymentAmount:
            settings = await db.settings.find_one()
            paymentAmount = settings.get("paymentAmount", 100000) if settings else 100000

        # Check if referral is used
        final_amount = paymentAmount
        yayasan_info = None
        if referralCode:
            yayasan = await db.yayasan.find_one({"referralCode": referralCode, "isActive": True})
            if yayasan:
                final_amount = yayasan.get("referralPrice", paymentAmount)
                yayasan_info = {"yayasanId": str(yayasan["_id"]), "yayasanName": yayasan.get("name")}

        # Create payment record
        payment_doc = {
            "userId": str(current_user["_id"]),
            "userEmail": current_user.get("email"),
            "userName": current_user.get("fullName", ""),
            "paymentType": paymentType,
            "paymentMethod": paymentMethod,
            "grossAmount": final_amount,
            "orderId": orderId or f"MANUAL-{uuid.uuid4().hex[:8].upper()}",
            "proofUrl": proof_url,
            "status": "pending",
            "referralCode": referralCode,
            "yayasanInfo": yayasan_info,
            "createdAt": datetime.utcnow()
        }

        result = await db.payment_proofs.insert_one(payment_doc)

        if paymentType == "test":
            await db.users.update_one(
                {"_id": current_user["_id"]},
                {"$set": {
                    "paymentStatus": "pending",
                    "paymentProofUrl": proof_url,
                    "paymentMethod": paymentMethod
                }}
            )

        return {
            "success": True,
            "paymentId": str(result.inserted_id),
            "proofUrl": proof_url,
            "message": "Bukti pembayaran berhasil diupload. Menunggu verifikasi admin."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/my-payments", response_model=List[dict])
async def get_my_payments(current_user: dict = Depends(get_current_user)):
    """Get current user's payment history"""
    try:
        cursor = db.payment_proofs.find({"userId": str(current_user["_id"])}).sort("createdAt", -1)
        payments = await cursor.to_list(100)
        for payment in payments:
            payment["_id"] = str(payment["_id"])
        return payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/test-price", response_model=dict)
async def get_test_price(referralCode: Optional[str] = None):
    """Get current test price from settings"""
    try:
        settings = await db.settings.find_one()
        base_price = settings.get("paymentAmount", 100000) if settings else 100000
        payment_instructions = settings.get("paymentInstructions", "Transfer ke rekening yang tertera") if settings else "Transfer ke rekening yang tertera"

        final_price = base_price
        is_yayasan_price = False
        yayasan_name = None

        if referralCode:
            yayasan = await db.yayasan.find_one({"referralCode": referralCode, "isActive": True})
            if yayasan:
                final_price = yayasan.get("referralPrice", base_price)
                is_yayasan_price = True
                yayasan_name = yayasan.get("name")

        return {
            "price": final_price,
            "basePrice": base_price,
            "requirePayment": settings.get("requirePayment", True) if settings else True,
            "paymentInstructions": payment_instructions,
            "isYayasanPrice": is_yayasan_price,
            "yayasanName": yayasan_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/status/{user_id}", response_model=dict)
async def get_payment_status(user_id: str):
    """Check if user has paid for premium test access"""
    try:
        approved_payment = await db.payment_proofs.find_one({
            "userId": user_id,
            "status": {"$in": ["approved", "paid", "settlement"]}
        })

        payment = await db.payments.find_one({
            "userId": user_id,
            "status": {"$in": ["approved", "paid", "settlement"]}
        })

        user = await db.users.find_one({"_id": ObjectId(user_id)})
        user_paid = False
        if user:
            user_paid = user.get("paymentStatus") in ["approved", "paid"] or \
                        user.get("paidTestStatus") == "completed" or \
                        user.get("hasPaidAccess") is True

        wallet_payment = await db.wallet_transactions.find_one({
            "userId": user_id,
            "type": "test_payment",
            "status": {"$in": ["success", "completed"]}
        })

        has_paid = approved_payment is not None or payment is not None or user_paid or wallet_payment is not None

        return {
            "status": "paid" if has_paid else "unpaid",
            "hasPaidAccess": has_paid,
            "message": "User memiliki akses test premium" if has_paid else "User belum membayar"
        }
    except Exception as e:
        return {"status": "unpaid", "hasPaidAccess": False, "message": f"Error: {str(e)}"}


@router.post("/paydisini/callback", response_model=dict)
async def paydisini_callback(request: Request):
    """Handle PayDisini payment callback/webhook"""
    try:
        form_data = await request.form()
        pay_id = form_data.get('pay_id')
        unique_code = form_data.get('unique_code')
        status_val = form_data.get('status')
        signature = form_data.get('signature')

        if not all([unique_code, status_val, signature]):
            return {"success": False, "message": "Missing required parameters"}

        # Verify signature
        if not paydisini_service.verify_callback(unique_code, signature):
            logger.warning(f"Invalid PayDisini callback signature for: {unique_code}")
            return {"success": False, "message": "Invalid signature"}

        # Update payment record
        payment = await db.payment_proofs.find_one({"orderId": unique_code})
        if payment:
            final_status = "approved" if status_val == "Success" else "failed"
            await db.payment_proofs.update_one(
                {"orderId": unique_code},
                {"$set": {"status": final_status, "updatedAt": datetime.utcnow(), "payId": pay_id}}
            )
            if final_status == "approved":
                await db.users.update_one(
                    {"_id": ObjectId(payment["userId"])},
                    {"$set": {"paymentStatus": "approved", "paymentDate": datetime.utcnow()}}
                )
                # Credit referral bonus
                if payment.get("referralCode"):
                    await credit_referral_bonus(payment["referralCode"], payment["userId"])

        return {"success": True}
    except Exception as e:
        logger.error(f"PayDisini callback error: {str(e)}")
        return {"success": False, "error": str(e)}


@router.get("/paydisini/status/{order_id}", response_model=dict)
async def check_paydisini_status(order_id: str, current_user: dict = Depends(get_current_user)):
    """Check payment status from PayDisini"""
    try:
        result = paydisini_service.check_payment_status(order_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/paydisini/channels", response_model=dict)
async def get_payment_channels():
    """Get available PayDisini payment channels"""
    try:
        result = paydisini_service.get_payment_channels()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


async def credit_referral_bonus(referral_code: str, referred_user_id: str):
    """Credit referral bonus when payment is successful"""
    try:
        referrer = await db.users.find_one({"myReferralCode": referral_code})
        if referrer:
            ref_settings = await db.referral_settings.find_one({})
            bonus_amount = ref_settings.get("bonusPerReferral", 10000) if ref_settings else 10000
            await db.referral_transactions.update_one(
                {"referrerId": str(referrer["_id"]), "referredId": referred_user_id, "status": "pending"},
                {"$set": {"status": "credited", "creditedAt": datetime.utcnow()}}
            )
            await db.users.update_one(
                {"_id": referrer["_id"]},
                {"$inc": {"referralBonus": bonus_amount}}
            )
            logger.info(f"Credited {bonus_amount} to referrer {referrer.get('email')}")
    except Exception as e:
        logger.error(f"Error crediting referral bonus: {str(e)}")
