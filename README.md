# Points System

A transaction tracking and ranking system built with FastAPI (Python) + plain HTML/JS frontend.

---

## How to Run

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server starts at `http://localhost:8000`

### Frontend

Just open `frontend/index.html` in your browser. No build step needed.

---

## API Docs

### POST /transaction

Adds points to a user account.

**Request body:**
```json
{
  "user_id": "u1",
  "amount": 200,
  "transaction_id": "txn-abc-001",
  "note": "referral bonus"
}
```

**Rules:**
- `amount` must be greater than 0
- `transaction_id` must be unique per transaction — duplicates are detected and skipped
- If `user_id` doesn't exist, the user is auto-created
- A threading lock ensures two simultaneous requests don't corrupt the same user's balance

---

### GET /summary/:userId

Returns stats for one user.

```json
{
  "user_id": "u1",
  "name": "Alice",
  "total_points": 450.0,
  "transaction_count": 3,
  "last_active": "2024-01-15T10:23:00"
}
```

Returns 404 if the user doesn't exist.

---

### GET /ranking

Returns all users sorted by a weighted score.

**Ranking formula:**
```
score = (0.7 × normalized_points) + (0.3 × normalized_transactions)
```

Points are normalized against the current max, same for transaction count. This means a user who makes many small transactions ranks higher than someone who made one huge transaction with the same total — it rewards consistent activity, not just big one-off deposits.

---

## How Duplicate Requests are Prevented

Every transaction comes with a caller-generated `transaction_id`. On the backend, all seen IDs are stored in a set. Before processing, we check if the ID already exists. If it does, we return a `skipped` status without applying any changes.

A `threading.Lock()` wraps the check + write together so two simultaneous requests with the same ID can't both slip through at the same moment.

---

## Data Storage

Everything is in-memory for now (a Python dict). Four users (u1–u4) are seeded on startup. In a real deployment this would be replaced with a proper database — Postgres most likely — and `seen_transactions` would be an indexed column rather than a set.

---

## Assumptions

- Transaction IDs are generated client-side (timestamp + counter). In production, the server would issue these.
- Points can only go up — no deductions or refunds in this version.
- Scores in the ranking update in real time on each `/ranking` call.
