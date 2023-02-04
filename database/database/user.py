from .base import *


class User(db.Model):
    __tablename__ = "user"

    email = Column(String, primary_key=True)
    password = Column(String)
    authenticated = Column(Boolean, default=False)

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
