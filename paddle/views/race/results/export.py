import tempfile
import csv
from flask_weasyprint import render_pdf

from ...common import *


@blueprint.route("/race/<race_id>/results/export/csv")
@login_required
def race_results_export_csv(race_id):
    race = session.get(db.Race, race_id)
    path = os.path.join(tempfile.mkdtemp(), race.slug + "-results.csv")

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

    with open(path, "w", newline="") as fid:
        writer = csv.writer(fid, quoting=csv.QUOTE_NONNUMERIC)
        for results in categories.values():
            for position, result in enumerate(results):
                writer.writerow(
                    [result.category, position + 1, str(result), result.time]
                )

    return send_file(path, as_attachment=True)


@blueprint.route("/race/<race_id>/results/export/pdf")
@login_required
def race_results_export_pdf(race_id):
    race = session.get(db.Race, race_id)
    return render_pdf(
        url_for("kanoe.race_results_paginated", race_id=race_id),
        download_filename=race.slug + "-results.pdf",
    )
