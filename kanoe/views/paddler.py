from .common import *


@blueprint.route("/paddlers", methods=("GET", "POST"))
def paddlers():
    if request.method == "POST":
        first = request.form["first"]
        middle = request.form["middle"]
        last = request.form["last"]
        division = request.form["division"]
        dob = request.form["dob"]
        title = request.form["title"]
        emergency_name = request.form["emergency_name"]
        emergency_phone = request.form["emergency_phone"]

        if dob:
            dob = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        else:
            dob = None

        if middle == "":
            middle = None
        if title == "":
            title = None

        if not first:
            flash("First name is required!", "danger")
        elif not last:
            flash("Last name is required!", "danger")
        elif not division:
            flash("Division is required!", "danger")
        else:
            paddler = db.Paddler(
                first=first,
                middle=middle,
                last=last,
                division=division,
                dob=dob,
                title=title,
                emergency_name=emergency_name,
                emergency_phone=emergency_phone,
            )
            session.add(paddler)
            session.commit()

            flash("Added a new paddler.", "success")

            return redirect(url_for("kanoe.paddlers"))

    paddlers = session.query(db.Paddler).all()
    return render_template("paddlers.j2", paddlers=paddlers)


@blueprint.route("/paddler/<paddler_id>")
def paddler(paddler_id):
    paddler = session.query(db.Paddler).get(paddler_id)
    return render_template("paddler.j2", paddler=paddler)
