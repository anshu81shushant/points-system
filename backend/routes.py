from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models import User, db_lock, seen_transactions, users

router = APIRouter()

# Indian Standard Time
IST = timezone(timedelta(hours=5, minutes=30))


class TxnPayload(BaseModel):
    user_id: str
    name: str = ""
    amount: float = Field(..., gt=0)
    transaction_id: str
    note: str = ""


@router.post("/transaction")
def add_transaction(payload: TxnPayload):

    if not payload.user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")

    if not payload.transaction_id.strip():
        raise HTTPException(status_code=400, detail="transaction_id is required")

    with db_lock:

        # duplicate transaction check
        if payload.transaction_id in seen_transactions:
            return {
                "status": "skipped",
                "reason": "transaction already processed",
                "transaction_id": payload.transaction_id,
            }

        # create new user if not exists
        if payload.user_id not in users:

            display_name = payload.name.strip() if payload.name.strip() else payload.user_id

            # block duplicate names
            existing_names = [u.name.lower() for u in users.values()]
            if display_name.lower() in existing_names:
                raise HTTPException(
                    status_code=400,
                    detail=f"A user named '{display_name}' already exists. Use a different name or the existing user ID."
                )

            users[payload.user_id] = User(payload.user_id, display_name)

        # apply points
        u = users[payload.user_id]
        u.total_points += payload.amount
        u.transaction_count += 1
        u.last_active = datetime.now(IST).strftime("%d %b %Y, %I:%M %p")
        seen_transactions.add(payload.transaction_id)

    return {
        "status": "ok",
        "user_id": payload.user_id,
        "points_added": payload.amount,
        "new_total": u.total_points,
    }


@router.get("/summary/{user_id}")
def user_summary(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail=f"No user found with id '{user_id}'")

    u = users[user_id]
    return {
        "user_id": u.user_id,
        "name": u.name,
        "total_points": u.total_points,
        "transaction_count": u.transaction_count,
        "last_active": u.last_active or "never",
    }


@router.get("/ranking")
def ranking():
    with db_lock:
        all_users = list(users.values())

    if not all_users:
        return {"ranking": []}

    max_pts = max(u.total_points for u in all_users) or 1
    max_txn = max(u.transaction_count for u in all_users) or 1

    def compute_score(u: User) -> float:
        # 70% total points, 30% number of transactions
        pts_norm = u.total_points / max_pts
        txn_norm = u.transaction_count / max_txn
        return round(0.7 * pts_norm + 0.3 * txn_norm, 4)

    ranked = sorted(all_users, key=compute_score, reverse=True)

    return {
        "ranking": [
            {
                "rank": idx + 1,
                "user_id": u.user_id,
                "name": u.name,
                "total_points": u.total_points,
                "transactions": u.transaction_count,
                "score": compute_score(u),
            }
            for idx, u in enumerate(ranked)
        ]
    }