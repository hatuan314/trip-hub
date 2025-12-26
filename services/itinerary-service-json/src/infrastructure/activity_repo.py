import json
import os
import uuid

FILE = "data/activities.json"


class ActivityRepo:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(FILE):
            with open(FILE, "w") as f:
                json.dump([], f)

    def _read(self):
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _write(self, data):
        with open(FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def create(self, username, payload):
        data = self._read()
        item = {"id": str(uuid.uuid4()), "user": username, **payload.dict()}
        data.append(item)
        self._write(data)
        return item

    def list_by_itinerary(self, username, itinerary_id):
        return [
            a
            for a in self._read()
            if a["user"] == username and a["itinerary_id"] == itinerary_id
        ]
