from .base import *


CATEGORY_LIST = [
    "K2 senior",
    "K2 Junior",
    "K2 Ladies",
    "K2 Veteran",
    "K2 Mixed",
    "K1 Senior",
    "K1 Junior",
    "K1 Ladies",
    "K1 Veteran",
    "Junior/Veteran",
    "C2",
    "C1",
]


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    label = Column(String)

    def __repr__(self):
        return "Category('%s')" % (self.label)
