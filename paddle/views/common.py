import datetime
import json
import logging
import os
import re

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename

import database as db

from .util import *

session = db.Session()

blueprint = Blueprint("kanoe", __name__, url_prefix="/")

AGE_GROUP_LOOKUP = {
    group.label[0]: group.id for group in session.query(db.AgeGroup).all()
}
