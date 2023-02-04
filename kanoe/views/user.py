import logging
from flask_login import login_required, login_user
from flask_bcrypt import check_password_hash

from .common import *
from .util import is_safe_url
from ..forms.login import LoginForm, RegisterForm


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
        flash(f"Account Succesfully created", "success")
        return redirect(url_for("kanoe.login"))

    return render_template("login.j2", form=form)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = session.query(db.User).filter_by(email=form.email.data).first()
        if check_password_hash(user.pwd, form.pwd.data):
            login_user(user)
            return redirect(url_for("kanoe.index"))
        else:
            flash("Invalid Username or password!", "danger")

    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    # form = LoginForm()
    # if form.validate_on_submit():
    #     # Login and validate the user.
    #     # user should be an instance of your `User` class
    #     login_user(user)

    #     flask.flash("Logged in successfully.")

    #     next = flask.request.args.get("next")
    #     # is_safe_url should check if the url is safe for redirects.
    #     # See http://flask.pocoo.org/snippets/62/ for an example.
    #     if not is_safe_url(next):
    #         return flask.abort(400)

    #     return flask.redirect(next or flask.url_for("index"))
    # return flask.render_template("login.html", form=form)

    return render_template("login.j2", form=form)


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(somewhere)
