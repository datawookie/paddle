from flask_login import UserMixin

from .base import *


class User(UserMixin, Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    pwd = Column(String)
    authenticated = Column(Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}')"
