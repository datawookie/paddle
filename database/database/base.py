import sys
import sqlalchemy
from sqlalchemy.orm import (
    sessionmaker,
    scoped_session,
    relationship,
    backref,
    reconstructor,
)
from sqlalchemy.orm import joinedload, lazyload, noload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Enum,
    Column,
    Integer,
    BigInteger,
    Numeric,
    String,
    Date,
    DateTime,
    Interval,
    Boolean,
    Text,
    JSON,
    ForeignKey,
    TIMESTAMP,
)
from sqlalchemy import MetaData, Index
from sqlalchemy.sql import func, expression
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.exc import SQLAlchemyError, DataError
from sqlalchemy.orm.exc import NoResultFound

from .config import *

CONNECTION_STRING = "sqlite:///kanoe.db"
CONNECTION_ARGS = {}

LIMIT_DAILY = sqlalchemy.text("1000")
UUID_GENERATE_V4 = sqlalchemy.text("uuid_generate_v4()")
FALSE = sqlalchemy.text("false")

engine = sqlalchemy.create_engine(
    CONNECTION_STRING,
    connect_args=CONNECTION_ARGS,
    echo=False,  # Set to True to get SQL statements.
)

session_factory = sessionmaker(
    bind=engine,
    autoflush=True,
)
Session = scoped_session(session_factory)

# ---------------------------------------------------------------------------------------------------------------------

Base = declarative_base(
    # metadata=MetaData(schema="public")
)
