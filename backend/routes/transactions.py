from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from datetime import datetime
from bson import ObjectId
from routes.admin import verify_token
import uuid
import logging

router = APIRouter(prefix="/api/transactions", tags=["transactions"])
db = get_db()
logger = logging.getLogger(__name__)


class ItemDetails(BaseModel):
    id: str
    price: int
    quantity: int
    name: str


class CustomerDetails(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: str
    phone: str


class TransactionRequest(BaseModel):
    order_id: str
    gross_amount: int
    items: List[ItemDetails]
    customer: CustomerDetails


@router.get("", response_model=List[dict])
async def get_transactions(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    token_data: dict = Depends(verify_token)
):
    """Get all transactions (admin only)"""
    try:
        query = {}
        if status:
            query["status"] = status
        cursor = db.transactions.find(query).skip(skip).limit(limit).sort("created_at", -1)
        transactions = await cursor.to_list(length=limit)
        for txn in transactions:
            txn["_id"] = str(txn["_id"])
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/stats/summary", response_model=dict)
async def get_transaction_stats(token_data: dict = Depends(verify_token)):
    """Get transaction statistics (admin only)"""
    try:
        total = await db.transactions.count_documents({})
        pending = await db.transactions.count_documents({"status": "pending"})
        settlement = await db.transactions.count_documents({"status": "settlement"})
        expired = await db.transactions.count_documents({"status": "expire"})

        pipeline = [
            {"$match": {"status": "settlement"}},
            {"$group": {"_id": None, "totalRevenue": {"$sum": "$gross_amount"}}}
        ]
        revenue_result = await db.transactions.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]["totalRevenue"] if revenue_result else 0

        return {
            "total": total,
            "pending": pending,
            "settlement": settlement,
            "expired": expired,
            "totalRevenue": total_revenue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/{order_id}/status", response_model=dict)
async def get_transaction_status(order_id: str):
    """Get transaction status"""
    try:
        transaction = await db.transactions.find_one({"order_id": order_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {
            "order_id": order_id,
            "status": transaction.get('status'),
            "payment_type": transaction.get('payment_type'),
            "gross_amount": transaction.get('gross_amount')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
