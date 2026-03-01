"""PayDisini Payment Gateway Service"""
import hashlib
import os
import uuid
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

PAYDISINI_API_KEY = os.environ.get("PAYDISINI_API_KEY", "")
PAYDISINI_BASE_URL = os.environ.get("PAYDISINI_BASE_URL", "https://api.paydisini.co.id/v1/")

QRIS_SERVICE_ID = "17"
QRIS_VALID_TIME = "300"  # 5 menit


def _signature_new_transaction(unique_code: str, service: str, amount: int, valid_time: str) -> str:
    """Signature untuk request 'new' transaction — sesuai PHP reference"""
    raw = PAYDISINI_API_KEY + unique_code + service + str(amount) + valid_time + "NewTransaction"
    return hashlib.md5(raw.encode()).hexdigest()


def _signature_status(unique_code: str) -> str:
    """Signature untuk cek status / callback"""
    raw = PAYDISINI_API_KEY + unique_code + "CallbackStatus"
    return hashlib.md5(raw.encode()).hexdigest()


def create_qris(amount: int, note: str = "") -> Dict[str, Any]:
    """
    Buat transaksi QRIS PayDisini — service=17
    Signature: md5(key + unique_code + service + amount + valid_time + 'NewTransaction')
    """
    unique_code = "pd_" + uuid.uuid4().hex[:12]
    sig = _signature_new_transaction(unique_code, QRIS_SERVICE_ID, amount, QRIS_VALID_TIME)

    payload = {
        "key": PAYDISINI_API_KEY,
        "request": "new",
        "unique_code": unique_code,
        "service": QRIS_SERVICE_ID,
        "amount": amount,
        "note": note or f"payment qris {amount}",
        "valid_time": QRIS_VALID_TIME,
        "type_fee": "2",
        "signature": sig,
    }

    logger.info(f"PayDisini QRIS create: unique_code={unique_code} amount={amount}")
    try:
        resp = requests.post(PAYDISINI_BASE_URL, data=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        logger.info(f"PayDisini QRIS response: success={data.get('success')} msg={data.get('msg')}")
        return {"unique_code": unique_code, **data}
    except requests.exceptions.RequestException as e:
        logger.error(f"PayDisini QRIS error: {e}")
        raise


def check_payment_status(unique_code: str) -> Dict[str, Any]:
    """Cek status pembayaran"""
    payload = {
        "key": PAYDISINI_API_KEY,
        "request": "status",
        "unique_code": unique_code,
        "signature": _signature_status(unique_code),
    }
    try:
        resp = requests.post(PAYDISINI_BASE_URL, data=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"PayDisini status error: {e}")
        raise


def cancel_payment(unique_code: str) -> Dict[str, Any]:
    """Batalkan transaksi"""
    payload = {
        "key": PAYDISINI_API_KEY,
        "request": "cancel",
        "unique_code": unique_code,
        "signature": _signature_status(unique_code),
    }
    try:
        resp = requests.post(PAYDISINI_BASE_URL, data=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"PayDisini cancel error: {e}")
        raise


def verify_callback(unique_code: str, provided_signature: str) -> bool:
    """Verifikasi signature dari callback PayDisini"""
    return _signature_status(unique_code) == provided_signature
