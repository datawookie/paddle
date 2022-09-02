from .base import *
from .race import *
from .category import *
from .series import *
import enum


class BoatType(enum.Enum):
    K1 = 1
    K2 = 2
    C = 3


boat_type = Enum(BoatType)


class Entry(Base):
    __tablename__ = "entry"

    id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey(Race.id), index=True)
    category_id = Column(Integer, ForeignKey(Category.id), index=True)
    series_id = Column(Integer, ForeignKey(Series.id), index=True)
    boat_type = Column(boat_type, index=True)
    entry_number = Column(Integer)

    # paddlers = relationship("Paddler", backref="entry")

    def __repr__(self):
        return "Entry(%d)" % (self.entry_number)


# class OptionContractExpiry(Base):
#     __tablename__ = "option_contract_expiry"
#     __table_args__ = (
#         UniqueConstraint(
#             "symbol", "expiry", name="unique_option_contract_expiry_symbol_expiry"
#         ),
#     )

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     # symbol = Column(String(8), ForeignKey(Symbol.id), index=True)
#     expiry = Column(Date(), index=True)

#     created_at = Column(TIMESTAMP, server_default=func.now())

#     def __repr__(self):
#         return "OptionContractExpiry(%d, '%s', '%s', '%s')" % (
#             self.id,
#             self.symbol,
#             self.expiry,
#             self.contract,
#         )


# class Option(Base):
#     __tablename__ = "option"
#     __table_args__ = (
#         UniqueConstraint(
#             "symbol", "label", "hour", name="unique_option_symbol_label_hour"
#         ),
#     )

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     symbol = Column(String(8), ForeignKey(Symbol.id), index=True)

#     right = Column(String(1))
#     expiry = Column(Date(), index=True)
#     label = Column(String(15), nullable=False)
#     strike = Column(Numeric(), nullable=False)
#     hour = Column(DateTime())
#     open = Column(Numeric())
#     high = Column(Numeric())
#     low = Column(Numeric())
#     close = Column(Numeric())

#     created_at = Column(TIMESTAMP, server_default=func.now())

#     def __repr__(self):
#         return "Option(%d, '%s', '%s', '%f')" % (
#             self.id,
#             self.symbol,
#             self.label,
#             self.strike,
#         )


# class OptionDaily(Base):
#     __tablename__ = "option_daily"
#     __table_args__ = (
#         UniqueConstraint(
#             "symbol", "date", "right", "expiry", "strike", name="unique_option_daily"
#         ),
#     )

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     symbol = Column(String(8), ForeignKey(Symbol.id), index=True)
#     date = Column(Date(), index=True)
#     right = Column(String(1))
#     expiry = Column(Date(), index=True)
#     strike = Column(Numeric(), nullable=False)
#     underlying = Column(Numeric(), nullable=True)
#     moneyness = Column(Enum(Moneyness), index=True)
#     price = Column(Numeric())
#     volatility_implied = Column(Numeric(), nullable=True)
#     historical = Column(Boolean, server_default=expression.false())

#     created_at = Column(TIMESTAMP, server_default=func.now())


# class OptionDailySpread(Base):
#     __tablename__ = "option_daily_spread"
#     __table_args__ = (
#         UniqueConstraint(
#             "symbol", "expiry", "strike", "date", name="unique_option_daily_spread"
#         ),
#     )

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     symbol = Column(String(8), ForeignKey(Symbol.id), index=True)

#     expiry = Column(Date(), index=True)
#     strike = Column(Numeric(), nullable=False)
#     date = Column(Date())
#     spread = Column(Numeric())

#     created_at = Column(TIMESTAMP, server_default=func.now())
