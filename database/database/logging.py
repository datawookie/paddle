import sys
import logging

# Enable detailed logging of SQL statements.
#
# This will just require that the logging level is INFO or lower.
#
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
# logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)

logging.getLogger("werkzeug").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s [%(levelname)8s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
)
#
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
