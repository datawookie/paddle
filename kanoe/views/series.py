from .common import *


@blueprint.route("/series/create", methods=("GET", "POST"))
def series_create():
    if request.method == "POST":
        name = request.form.get("name")

        series = db.Series(name=name)
        session.add(series)
        session.commit()

        return redirect(url_for("kanoe.races"))

    return render_template("series-create.j2")
