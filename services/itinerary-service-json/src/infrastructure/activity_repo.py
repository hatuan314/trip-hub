import uuid


class ActivityRepo:
    def __init__(self, session):
        self.session = session

    def create(self, username, payload):
        from src.infrastructure.database.models import Activity

        item = Activity(
            id=str(uuid.uuid4()),
            itinerary_id=payload.itinerary_id,
            username=username,
            title=payload.title,
            start_time=payload.start_time,
            end_time=payload.end_time,
            location=payload.location,
            note=payload.note,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return {
            "id": item.id,
            "user": item.username,
            "itinerary_id": item.itinerary_id,
            "title": item.title,
            "start_time": item.start_time.isoformat(),
            "end_time": item.end_time.isoformat(),
            "location": item.location,
            "note": item.note,
        }

    def list_by_itinerary(self, username, itinerary_id):
        from src.infrastructure.database.models import Activity

        rows = (
            self.session.query(Activity)
            .filter(Activity.username == username, Activity.itinerary_id == itinerary_id)
            .order_by(Activity.created_at.desc())
            .all()
        )
        return [
            {
                "id": row.id,
                "user": row.username,
                "itinerary_id": row.itinerary_id,
                "title": row.title,
                "start_time": row.start_time.isoformat(),
                "end_time": row.end_time.isoformat(),
                "location": row.location,
                "note": row.note,
            }
            for row in rows
        ]
