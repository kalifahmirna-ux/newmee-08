"""PayDisini Payment Gateway Service"""
import hashlib
import os
import uuid
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

PAYDISINI_API_KEY = os.environ.get("PAYDISINI_API_KEY", "")
PAYDISINI_API_ID = os.environ.get("PAYDISINI_API_ID", "")
PAYDISINI_BASE_URL = os.environ.get("PAYDISINI_BASE_URL", "https://api.paydisini.co.id/v1/")


def generate_signature(unique_code: str) -> str:
    """Generate MD5 signature for PayDisini requests"""
    signature_string = PAYDISINI_API_KEY + unique_code + "CallbackStatus"
    return hashlib.md5(signature_string.encode()).hexdigest()


def create_payment(
    unique_code: str,
    service: str,
    amount: float,
    note: str,
    expired: int = 24,
    type_fee: int = 1,
    callback_url: Optional[str] = None
) -> Dict[str, Any]:
    """Create payment transaction with PayDisini"""
    payload = {
        'key': PAYDISINI_API_KEY,
        'request': 'transaction',
        'unique_code': unique_code,
        'service': service,
        'amount': int(amount),
        'note': note,
        'expired': expired,
        'type_fee': type_fee,
        'signature': hashlib.md5(
            (PAYDISINI_API_KEY + unique_code + str(service) + str(int(amount)) + "NOW").encode()
        ).hexdigest()
    }
    if callback_url:
        payload['return_url'] = callback_url

    try:
        response = requests.post(PAYDISINI_BASE_URL, data=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        logger.info(f"PayDisini create payment: unique_code={unique_code}, success={data.get('success')}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"PayDisini API error: {str(e)}")
        raise


def check_payment_status(unique_code: str) -> Dict[str, Any]:
    """Check payment status from PayDisini"""
    payload = {
        'key': PAYDISINI_API_KEY,
        'request': 'status',
        'unique_code': unique_code,
        'signature': generate_signature(unique_code)
    }
    try:
        response = requests.post(PAYDISINI_BASE_URL, data=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"PayDisini status check error: {str(e)}")
        raise


def cancel_payment(unique_code: str) -> Dict[str, Any]:
    """Cancel a payment transaction"""
    payload = {
        'key': PAYDISINI_API_KEY,
        'request': 'cancel',
        'unique_code': unique_code,
        'signature': generate_signature(unique_code)
    }
    try:
        response = requests.post(PAYDISINI_BASE_URL, data=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"PayDisini cancel error: {str(e)}")
        raise


def get_payment_channels() -> Dict[str, Any]:
    """Get available payment channels"""
    payload = {
        'key': PAYDISINI_API_KEY,
        'request': 'payment_channel',
        'signature': hashlib.md5((PAYDISINI_API_KEY + "payment_channel").encode()).hexdigest()
    }
    try:
        response = requests.post(PAYDISINI_BASE_URL, data=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"PayDisini channels error: {str(e)}")
        raise


def verify_callback(unique_code: str, provided_signature: str) -> bool:
    """Verify callback signature from PayDisini"""
    expected = generate_signature(unique_code)
    return expected == provided_signature
