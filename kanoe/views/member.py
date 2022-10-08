from .common import *


@blueprint.route("/time-trial")
def time_trial():
    members = session.query(db.Member).all()
    return render_template("time-trial.j2", members=members)


@blueprint.route("/member/<member_id>")
def member(member_id):
    member = session.query(db.Member).get(member_id)
    return render_template("member.j2", member=member)
