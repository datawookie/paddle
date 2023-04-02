from ...common import *
from ...util import argument_boolean


@blueprint.route("/race/<race_id>/results/category", methods=("GET", "POST"))
def race_results_category(race_id):
    race = session.get(db.Race, race_id)
    categories = session.query(db.Category).all()
    category = None
    results = None

    if request.method == "POST":
        category_id = int(request.form.get("category_id"))
        category = session.get(db.Category, category_id)

        results = (
            session.query(db.Entry)
            .filter(db.Entry.race_id == race_id)
            .filter(db.Entry.time_start.is_not(None))
            .filter(db.Entry.time_finish.is_not(None))
            .filter(db.Entry.category_id == category_id)
            .all()
        )

        # Sort by finish time.
        results.sort(key=lambda x: x.time, reverse=False)

        # Keep only top 10.
        results = results[:10]

    return render_template(
        "race-results-category.j2",
        race=race,
        category=category,
        categories=categories,
        results=results,
    )


@blueprint.route("/race/<race_id>/results/scrolling")
def race_results_scrolling(race_id):
    scrolling = argument_boolean(request.args.get("scrolling", 0))
    try:
        # ?category -> Show category selector.
        # ?category=<category_id> -> Show category selector and selected category.
        #
        category = request.args["category"]
        if category == "":
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
    #
    if isinstance(category, db.Category):
        # Filter selected category.
        for key in list(data.keys()):
            if key != category.label:
                del data[key]

    # Sort results in each category.
    for results in data.values():
        results.sort(key=lambda x: x.time, reverse=False)

    announcements = session.query(db.Announcement).filter(db.Announcement.enabled).all()

    return render_template(
        "race-results-scrolling.j2",
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
