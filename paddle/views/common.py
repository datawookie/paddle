import os
import json
import datetime
import re
import logging
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    flash,
    redirect,
    jsonify,
    abort,
    send_file,
)
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.sql import func

import database as db

from .util import *

session = db.Session()

blueprint = Blueprint("kanoe", __name__, url_prefix="/")