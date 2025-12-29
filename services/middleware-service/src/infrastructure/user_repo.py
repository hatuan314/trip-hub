class UserRepo:
    def __init__(self, session):
        self.session = session

    def create(self, username, password):
        from src.infrastructure.database.models import User

        user = User(username=username, password=password)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return {"username": user.username, "password": user.password}

    def get(self, username):
        from src.infrastructure.database.models import User

        user = self.session.query(User).filter(User.username == username).first()
        if not user:
            return None
        return {"username": user.username, "password": user.password}
