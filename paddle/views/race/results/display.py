from ...common import *
from ...util import argument_boolean


@blueprint.route("/race/<race_id>/results", methods=("GET", "POST"))
def race_results(race_id):
    if request.method == "POST":
        # Process category selection from form.
        category = int(request.form.get("category"))
        return redirect(
            url_for("kanoe.race_results", race_id=race_id, category=category)
        )

    scrolling = argument_boolean(request.args.get("scrolling", 0))
    try:
        # ?category -> Show category selector.
        # ?category=<category_id> -> Show category selector and selected category.
        #
        category = request.args["category"]
        if category == "" or category == "0":
            category = True
        else:
            category = session.get(db.Category, category)
    except KeyError:
        category = False

    if category:
        scrolling = False

    categories = session.query(db.Category).all()
    race = session.get(db.Race, race_id)
    results = (
        session.query(db.Entry)
        .filter(db.Entry.race_id == race_id)
        .filter(db.Entry.time_start.is_not(None))
        .filter(db.Entry.time_finish.is_not(None))
        .all()
    )

    data = db.entries_get_categories(results)
    # Filter selected category.
    if isinstance(category, db.Category):
        for key in list(data.keys()):
            if key != category.label:
                del data[key]
    elif category:
        data = {}

    # Sort results in each category.
    for results in data.values():
        results.sort(key=lambda x: x.time, reverse=False)

    announcements = session.query(db.Announcement).filter(db.Announcement.enabled).all()

    return render_template(
        "race-results.j2",
        scrolling=scrolling,
        category=category,
        categories=categories,
        race=race,
        data=data,
        announcements=announcements,
    )


@blueprint.route("/race/<race_id>/results/validate")
@login_required
def race_results_validate(race_id):
    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()
    race = session.get(db.Race, race_id)
    return render_template(
        "race-results-validate.j2",
        race=race,
        entries=entries,
        time_between=time_between,
    )


@blueprint.route("/race/<race_id>/results/paginated")
@login_required
def race_results_paginated(race_id):
    race = session.get(db.Race, race_id)

    results = (
        session.query(db.Entry)
        .filter(db.Entry.race_id == race_id)
        .filter(db.Entry.time_start.is_not(None))
        .filter(db.Entry.time_finish.is_not(None))
        .all()
    )

    categories = db.entries_get_categories(results)

    # Sort results in each category.
    for results in categories.values():
        results.sort(key=lambda x: x.time, reverse=False)

    return render_template(
        "race-results-paginated.j2",
        race=race,
        categories=categories,
        timestamp=datetime.datetime.now(),
    )
