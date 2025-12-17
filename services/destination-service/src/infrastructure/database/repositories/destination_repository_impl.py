from sqlalchemy.orm import Session
from src.core.interfaces.destination_repository import DestinationRepository
from src.core.entities.destination import Destination
from src.infrastructure.database import models


class SqlAlchemyDestinationRepository(DestinationRepository):
    def __init__(self, session: Session):
        self.session = session


    def list_destinations(self):
        return [Destination(id=row.id, name=row.name, country=row.country, description=row.description) for row in self.session.query(models.DestinationModel).all()]


    def get(self, destination_id: str):
        row = self.session.get(models.DestinationModel, destination_id)
        if row:
            return Destination(id=row.id, name=row.name, country=row.country, description=row.description)
        return None


    def list_attractions(self, destination_id: str):
        return []


    def list_hotels(self, destination_id: str):
        return []
