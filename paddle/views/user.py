import logging
from flask_bcrypt import check_password_hash

from .common import *
from ..forms.login import LoginForm, RegisterForm

from flask import session as flask_session


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    from kanoe import bcrypt

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        pwd = form.pwd.data

        logging.info(f"EMAIL: {email}")

        newuser = db.User(
            email=email,
            pwd=bcrypt.generate_password_hash(pwd),
        )

        session.add(newuser)
        session.commit()
        flash("Account Succesfully created", "success")
        return redirect(url_for("kanoe.login"))

    return render_template("login.j2", form=form)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = session.query(db.User).filter_by(email=form.email.data).first()
        if check_password_hash(user.pwd, form.pwd.data):
            login_user(user)
            flask_session["user"] = current_user.email
            return redirect(url_for("kanoe.index"))
        else:
            flash("Invalid Username or password!", "danger")

    return render_template("login.j2", form=form)


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flask_session["user"] = None
    return redirect(url_for("kanoe.index"))