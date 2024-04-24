import pandas as pd
import recordlinkage

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
    paddlers = session.query(db.Paddler).all()

    df = pd.DataFrame(
        [(paddler.first, paddler.middle, paddler.last) for paddler in paddlers],
        columns=["first", "middle", "last"],
    )

    df["first"] = df["first"].str.lower()
    df["middle"] = df["middle"].str.lower()
    df["last"] = df["last"].str.lower()

    indexer = recordlinkage.Index()
    indexer.full()
    candidate_links = indexer.index(df)

    compare = recordlinkage.Compare()

    compare.exact("last", "last", label="last")
    compare.string(
        "first", "first", method="jarowinkler", threshold=0.85, label="first"
    )
    compare.string(
        "middle", "middle", method="jarowinkler", threshold=0.85, label="middle"
    )

    features = compare.compute(candidate_links, df)

    potential_duplicates = features[features.sum(axis=1) > 1]

    duplicates = [(paddlers[i], paddlers[j]) for i, j in potential_duplicates.index]

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

    membership_bodies = session.query(db.MembershipBody).all()

    if request.method == "POST":
        first = request.form["first"]
        middle = request.form["middle"]
        last = request.form["last"]
        gender = request.form["gender"]
        division = request.form["division"]
        dob = request.form["dob"]
        age_group_id = request.form["age_group_id"]
        title = request.form["title"]
        emergency_name = request.form["emergency_name"]
        emergency_phone = request.form["emergency_phone"]
        membership_number = request.form["membership_number"]
        membership_expiry = request.form["membership_expiry"]
        membership_body_id = request.form["membership_body_id"]

        if dob:
            dob = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        else:
            dob = None

        if membership_expiry:
            membership_expiry = datetime.datetime.strptime(
                membership_expiry, "%Y-%m-%d"
            ).date()
        else:
            membership_expiry = None

        age_group_id = empty_to_none(age_group_id)
        first = empty_to_none(first)
        middle = empty_to_none(middle)
        last = empty_to_none(last)
        title = empty_to_none(title)
        membership_number = empty_to_none(membership_number)
        division = empty_to_none(division)
        emergency_name = empty_to_none(emergency_name)
        emergency_phone = empty_to_none(emergency_phone)
        membership_body_id = empty_to_none(membership_body_id)

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
                paddler.gender = gender
                paddler.division = division
                paddler.dob = dob
                paddler.age_group_id = age_group_id
                paddler.title = title
                paddler.emergency_name = emergency_name
                paddler.emergency_phone = emergency_phone
                paddler.membership_number = membership_number
                paddler.membership_expiry = membership_expiry
                paddler.membership_body_id = membership_body_id

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
                    membership_number=membership_number,
                    membership_expiry=membership_expiry,
                    membership_body_id=membership_body_id,
                )
                session.add(paddler)

                flash("Added a new paddler.", "success")

            session.commit()

            return redirect(url_for("paddle.paddlers"))

    if paddler:
        logging.debug(f"* {repr(paddler)}")
        logging.debug("  Crews:")
        for crew in paddler.crews:
            logging.debug(f"    - {repr(crew)}")

    paddler.crews = sorted(paddler.crews, key=lambda c: c.entry.race.date, reverse=True)

    return render_template(
        "paddler.j2",
        paddler=paddler,
        age_groups=age_groups,
        membership_bodies=membership_bodies,
    )
