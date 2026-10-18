"""Isolated Billing Service module."""


class BillingService:
    def __init__(self):
        self.accounts = {"alice": 150.0, "bob": 45.0}

    def get_balance(self, username: str) -> float:
        return self.accounts.get(username, 0.0)

    def charge(self, username: str, amount: float) -> bool:
        if amount <= 0:
            return False
        balance = self.accounts.get(username, 0.0)
        if balance >= amount:
            self.accounts[username] = balance - amount
            return True
        return False
