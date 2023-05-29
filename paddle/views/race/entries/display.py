from ...common import *


@blueprint.route("/race/<race_id>/entries/display")
@login_required
def race_entries_display(race_id):
    race = session.get(db.Race, race_id)

    entries = session.query(db.Entry).filter(db.Entry.race_id == race_id).all()

    categories = db.entries_get_categories(entries)
    # Sort by last name of first paddler in crew.
    for entries in categories.values():
        entries.sort(key=lambda x: x.crews[0].paddler.last, reverse=False)

    return render_template(
        "race-entries-display.j2",
        race=race,
        categories=categories,
    )
