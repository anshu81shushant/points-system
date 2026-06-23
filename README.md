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
# Points System

## Demo Video
[Click here to watch the demo](https://drive.google.com/drive/folders/1TzzEYjuKY9mD_k3M7bBSeLaOBENm6o7t?usp=sharing)

---

## How to Run

### Backend
cd backend
pip install -r requirements.txt
python main.py

Server starts at http://localhost:8000

### Frontend
Open frontend/index.html in your browser directly. No build step needed.

---

## API Docs

### POST /transaction
Adds points to a user account.

Request body example:
{
  "user_id": "u1",
  "name": "John",
  "amount": 300,
  "transaction_id": "txn-u1-001",
  "note": "referral bonus"
}

Rules:
- amount must be greater than 0
- user_id cannot be empty
- if transaction_id was already used, request is skipped silently
- if a new user is being created, name must be unique
- if user_id already exists, points are simply added to their account

---

### GET /summary/:userId
Returns all details for a single user.

Response example:
{
  "user_id": "u1",
  "name": "John",
  "total_points": 300,
  "transaction_count": 1,
  "last_active": "23 Jun 2024, 04:30 PM"
}

Returns 404 error if user does not exist.

---

### GET /ranking
Returns all users sorted by their score.

Response example:
{
  "ranking": [
    {
      "rank": 1,
      "user_id": "u1",
      "name": "John",
      "total_points": 300,
      "transactions": 1,
      "score": 1.0
    }
  ]
}

---

## How Ranking is Calculated

The score is based on two factors so a single large transaction
cannot dominate the leaderboard.

score = (0.7 x normalized points) + (0.3 x normalized transactions)

- 70 percent weight goes to total points
- 30 percent weight goes to number of transactions
- Both values are normalized against the current highest value

Example:
- User A has 1000 points in 1 transaction
- User B has 800 points in 10 transactions
- User B may rank higher because of consistent activity

---

## How Duplicate Requests are Prevented

Every transaction includes a unique transaction_id generated on
the frontend using timestamp and a counter.

Before processing any transaction the backend checks if that ID
already exists in a set called seen_transactions.

If the ID is found the request is skipped and a skipped status
is returned without modifying any data.

A Python threading Lock wraps the check and the write together
so two requests arriving at the same millisecond cannot both
pass the check at the same time.

---

## How Concurrency is Handled

Python threading.Lock is used in two places.

1. When adding a transaction — the duplicate check and the
   point update both happen inside the same lock so data
   cannot be corrupted by simultaneous requests.

2. When reading the ranking — the user list is copied inside
   the lock so the sort always works on a consistent snapshot.

---

## Data Storage

All data is stored in memory using Python dictionaries.
This means data resets when the server restarts.

In a production system this would be replaced with a
database like PostgreSQL with proper indexed columns.

---

## Assumptions

- Transaction IDs are generated on the frontend
  In production the server should generate these

- Points can only go up, no deductions in this version

- Users are auto created on first transaction
  No separate registration step needed

- Time is stored and displayed in Indian Standard Time IST

---

## Project Structure

points-system/
├── backend/
│   ├── main.py         starts the server
│   ├── routes.py       all three APIs
│   ├── models.py       user data storage
│   └── requirements.txt
├── frontend/
│   └── index.html      the webpage
└── README.md
