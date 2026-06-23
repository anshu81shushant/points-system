import threading


class User:
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name
        self.total_points = 0.0
        self.transaction_count = 0
        self.last_active = ""


users: dict[str, User] = {}
seen_transactions: set[str] = set()
db_lock = threading.Lock()