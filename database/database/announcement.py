from .base import *


class Announcement(Base):
    __tablename__ = "announcement"

    id = Column(Integer, primary_key=True)
    text = Column(String)
    enabled = Column(Boolean)

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"Announcement(text='{self.text}')"
