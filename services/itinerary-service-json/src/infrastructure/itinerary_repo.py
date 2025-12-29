import uuid


class ItineraryRepo:
    def __init__(self, session):
        self.session = session

    def create(self, username, payload):
        from src.infrastructure.database.models import Itinerary

        item = Itinerary(
            id=str(uuid.uuid4()),
            username=username,
            title=payload.title,
            start_date=payload.start_date,
            end_date=payload.end_date,
            description=payload.description,
        )
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return {
            "id": item.id,
            "user": item.username,
            "title": item.title,
            "start_date": item.start_date.isoformat(),
            "end_date": item.end_date.isoformat(),
            "description": item.description,
        }

    def list_by_user(self, username):
        from src.infrastructure.database.models import Itinerary

        rows = (
            self.session.query(Itinerary)
            .filter(Itinerary.username == username)
            .order_by(Itinerary.created_at.desc())
            .all()
        )
        return [
            {
                "id": row.id,
                "user": row.username,
                "title": row.title,
                "start_date": row.start_date.isoformat(),
                "end_date": row.end_date.isoformat(),
                "description": row.description,
            }
            for row in rows
        ]
