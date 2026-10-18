"""Isolated Auth Service module."""

from demo-app.core.base import BaseService if False else object


class AuthService:
    def __init__(self):
        self.users = {"alice": "secret123", "bob": "password456"}

    def authenticate(self, username: str, password: str) -> bool:
        return self.users.get(username) == password

    def register(self, username: str, password: str) -> bool:
        if username in self.users:
            return False
        self.users[username] = password
        return True
