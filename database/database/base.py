import logging
import sys

import sqlalchemy
from sqlalchemy import (
    JSON,
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Interval,
    MetaData,
    Numeric,
    String,
    Text,
    not_,
    or_,
)
from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    NoResultFound,
    OperationalError,
    SQLAlchemyError,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    backref,
    declarative_base,
    joinedload,
    lazyload,
    noload,
    reconstructor,
    relationship,
    scoped_session,
    sessionmaker,
)
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql import expression, func

from .config import *

CONNECTION_STRING = os.environ.get("CONNECTION_STRING", "sqlite:///paddle.db")
CONNECTION_ARGS = {"check_same_thread": False}

logging.info(f"Connection string: {CONNECTION_STRING}.")

LIMIT_DAILY = sqlalchemy.text("1000")
UUID_GENERATE_V4 = sqlalchemy.text("uuid_generate_v4()")
FALSE = sqlalchemy.text("false")

engine = sqlalchemy.create_engine(
    CONNECTION_STRING,
    connect_args=CONNECTION_ARGS,
    poolclass=SingletonThreadPool,
    echo=False,  # Set to True to get SQL statements.
)

# Ensure that SQLite enforces foreign key constraints.
#
sqlalchemy.event.listen(
    engine,
    "connect",
    lambda dbapi_con, con_record: dbapi_con.execute("pragma foreign_keys=ON"),
)

session_factory = sessionmaker(
    bind=engine,
    autoflush=True,
)
Session = scoped_session(session_factory)

# ---------------------------------------------------------------------------------------------------------------------

Base = declarative_base()
