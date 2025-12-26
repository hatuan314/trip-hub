import json
import os

USER_FILE = "data/users.json"


class UserRepo:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(USER_FILE):
            with open(USER_FILE, "w") as f:
                json.dump({}, f)

    def _read(self):
        with open(USER_FILE, "r") as f:
            return json.load(f)

    def _write(self, data):
        with open(USER_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def create(self, username, password):
        users = self._read()
        users[username] = {"username": username, "password": password}
        self._write(users)

    def get(self, username):
        return self._read().get(username)
