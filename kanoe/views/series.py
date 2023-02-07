from flask_login import login_required

from .common import *


@blueprint.route("/series/create", methods=("GET", "POST"))
@login_required
def series_create():
    if request.method == "POST":
        name = request.form.get("name")

        series = db.Series(name=name)
        session.add(series)
        session.commit()

        return redirect(url_for("kanoe.races"))

    return render_template("series-create.j2")
