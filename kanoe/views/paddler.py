from .common import *


def empty_to_none(text):
    if text == "":
        return None
    else:
        return text


@blueprint.route("/paddlers")
def paddlers():
    paddlers = session.query(db.Paddler).all()
    return render_template("paddlers.j2", paddlers=paddlers)


@blueprint.route("/paddler/<paddler_id>", methods=("GET", "POST"))
@blueprint.route("/paddler/", defaults={"paddler_id": None}, methods=("GET", "POST"))
def paddler(paddler_id):
    if paddler_id:
        paddler = session.query(db.Paddler).get(paddler_id)
    else:
        paddler = None

    if request.method == "POST":
        first = request.form["first"]
        middle = request.form["middle"]
        last = request.form["last"]
        division = request.form["division"]
        dob = request.form["dob"]
        title = request.form["title"]
        emergency_name = request.form["emergency_name"]
        emergency_phone = request.form["emergency_phone"]
        bcu = request.form["bcu"]
        bcu_expiry = request.form["bcu_expiry"]

        if dob:
            dob = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        else:
            dob = None

        if bcu_expiry:
            bcu_expiry = datetime.datetime.strptime(bcu_expiry, "%Y-%m-%d").date()
        else:
            bcu_expiry = None

        if middle == "":
            middle = None
        if title == "":
            title = None
        if bcu == "":
            bcu = None

        if not first:
            flash("First name is required!", "danger")
        elif not last:
            flash("Last name is required!", "danger")
        # elif not division:
        #     flash("Division is required!", "danger")
        else:
            # Updating an existing paddler or creating a new one?
            #
            if paddler:
                # Update existing paddler.
                paddler.first = empty_to_none(first)
                paddler.middle = empty_to_none(middle)
                paddler.last = empty_to_none(last)
                paddler.division = empty_to_none(division)
                paddler.dob = empty_to_none(dob)
                paddler.title = empty_to_none(title)
                paddler.emergency_name = empty_to_none(emergency_name)
                paddler.emergency_phone = empty_to_none(emergency_phone)
                paddler.bcu = empty_to_none(bcu)
                paddler.bcu_expiry = empty_to_none(bcu_expiry)

                flash("Updated existing paddler.", "success")
            else:
                # Create new paddler.
                paddler = db.Paddler(
                    first=first,
                    middle=middle,
                    last=last,
                    division=division,
                    dob=dob,
                    title=title,
                    emergency_name=emergency_name,
                    emergency_phone=emergency_phone,
                    bcu=bcu,
                    bcu_expiry=bcu_expiry,
                )
                session.add(paddler)

                flash("Added a new paddler.", "success")

            session.commit()

            return redirect(url_for("kanoe.paddlers"))

    return render_template("paddler.j2", paddler=paddler)
