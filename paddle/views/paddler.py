from .common import *
from .util import empty_to_none


@blueprint.route("/paddlers")
@login_required
def paddlers():
    paddlers = session.query(db.Paddler).all()
    return render_template("paddlers.j2", paddlers=paddlers)


@blueprint.route("/paddlers/validate")
@login_required
def paddlers_validate():
    # Gather counts of paddlers grouped by first and last name.
    counts = (
        session.query(
            func.count(), db.Paddler.first, db.Paddler.middle, db.Paddler.last
        )
        .group_by(db.Paddler.first, db.Paddler.middle, db.Paddler.last)
        .order_by(db.Paddler.last)
        .all()
    )
    # Filter out entries which have a count > 1.
    counts = [count for count in counts if count[0] > 1]
    # Retrieve duplicated paddlers.
    duplicates = {}
    for count, first, middle, last in counts:
        name = db.combine_names(first, middle, last)
        duplicates[name] = (
            session.query(db.Paddler)
            .filter(
                db.Paddler.first == first,
                db.Paddler.middle == middle,
                db.Paddler.last == last,
            )
            .all()
        )
    return render_template("paddlers-validate.j2", duplicates=duplicates)


@blueprint.route("/paddler/<paddler_id>", methods=("GET", "POST"))
@blueprint.route("/paddler/", defaults={"paddler_id": None}, methods=("GET", "POST"))
@login_required
def paddler(paddler_id):
    if paddler_id:
        paddler = session.get(db.Paddler, paddler_id)
    else:
        paddler = None

    age_groups = session.query(db.AgeGroup).all()

    if request.method == "POST":
        first = request.form["first"]
        middle = request.form["middle"]
        last = request.form["last"]
        division = request.form["division"]
        dob = request.form["dob"]
        age_group_id = request.form["age_group_id"]
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

        age_group_id = empty_to_none(age_group_id)
        first = empty_to_none(first)
        middle = empty_to_none(middle)
        last = empty_to_none(last)
        title = empty_to_none(title)
        bcu = empty_to_none(bcu)
        division = empty_to_none(division)
        emergency_name = empty_to_none(emergency_name)
        emergency_phone = empty_to_none(emergency_phone)

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
                paddler.first = first
                paddler.middle = middle
                paddler.last = last
                paddler.division = division
                paddler.dob = dob
                paddler.age_group_id = age_group_id
                paddler.title = title
                paddler.emergency_name = emergency_name
                paddler.emergency_phone = emergency_phone
                paddler.bcu = bcu
                paddler.bcu_expiry = bcu_expiry

                flash("Updated existing paddler.", "success")
            else:
                # Create new paddler.
                paddler = db.Paddler(
                    first=first,
                    middle=middle,
                    last=last,
                    division=division,
                    dob=dob,
                    age_group_id=age_group_id,
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

    if paddler:
        logging.debug(f"* {repr(paddler)}")
        logging.debug("  Crews:")
        for crew in paddler.crews:
            logging.debug(f"    - {repr(crew)}")

    return render_template("paddler.j2", paddler=paddler, age_groups=age_groups)