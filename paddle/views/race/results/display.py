from ...common import *
from ...util import argument_boolean


def race_results(race_id, category_id=None, scrolling=True, top=None):
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
    if category_id is None:
        category = False
    else:
        category = session.get(db.Category, category_id)

        if category:
            for key in list(data.keys()):
                if key != category.label:
                    del data[key]
                else:
                    if top:
                        data[key] = data[key][:top]
        else:
            category = True
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


@blueprint.route("/race/<race_id>/results/category/", methods=("GET", "POST"))
def race_results_category(race_id):
    # Use ?top=<N> to specify how many results to show per category.
    top = int(request.args.get("top", 10))

    if request.method == "POST":
        # Process category selection from form.
        category_id = int(request.form.get("category"))
    else:
        category_id = 0

    return race_results(race_id, category_id=category_id, scrolling=False, top=top)


@blueprint.route("/race/<race_id>/results/scrolling")
def race_results_scrolling(race_id, scrolling=True):
    return race_results(race_id, scrolling=True)


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
