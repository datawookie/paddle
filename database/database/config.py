import os
from dotenv import load_dotenv

from .logging import logger

load_dotenv()

DBHOST = os.getenv("DBHOST")
DBNAME = os.getenv("DBNAME")
DBSCHEMA = os.getenv("DBSCHEMA")
DBUSER = os.getenv("DBUSER")
DBPASSWD = os.getenv("DBPASSWD")

logger.debug("Database details:")
logger.debug(f"- host:     {DBHOST}")
logger.debug(f"- name:     {DBNAME}")
logger.debug(f"- schema:   {DBSCHEMA}")
logger.debug(f"- user:     {DBUSER}")
if DBPASSWD:
    logger.debug(f"- password: {'*'*len(DBPASSWD)}")
