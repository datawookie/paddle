from .common import *

from .api import *
from .club import *
from .entry import *
from .member import *
from .paddler import *
from .race import *
from .crew import *
from .series import *
from .team import *


@blueprint.route("/")
def index():
    return render_template("index.j2")
