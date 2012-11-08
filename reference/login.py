"""

This is a small application that provides a login page for curators to view/edit the
information in Oracle database. This application is using Flask-Login package (created
by Matthew Frazier, MIT) for handling the login sessions and everything. 

"""

from flask import Flask, session, request, render_template, redirect, url_for, flash
from flask.ext.login import (LoginManager, current_user, login_required, login_user,
                             logout_user, confirm_login, fresh_login_required)

from config import (HOST, PORT, DBUSER, DBPASS, SECRET_KEY, DEBUG, Anonymous, USERS, USER_NAMES)
from models import (db, Database, RefTemp, RefBad, Reference)
from literature import ReferenceLink

app = Flask(__name__)

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(id):
    return USERS.get(int(id))


login_manager.setup_app(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reference")
@fresh_login_required
def reference():
    try:
#        app.stop()
#        app.run()
        refs = RefTemp.search()
    except:
        Database(DBUSER, DBPASS)
        refs = RefTemp.search()
    num_of_refs = len(refs.all())
    return render_template('literature_review.html',
                           ref_list=refs,
                           ref_count=num_of_refs)
    

@app.route("/reference/delete/<pmid>")
@fresh_login_required
def discard_ref(pmid):

    try:       
        RefTemp.delete(pmid)
        RefBad.insert(pmid, current_user.name.upper())
        db.session.commit()
    except:
        db.session.rollback()
        return "An error occurred when deleting the reference for pmid=" + pmid + " from the database."
    return "Reference for pmid=" + pmid + " has been removed from the database!"


@app.route("/reference/link/<pmid>/<parameters>")
@fresh_login_required
def link_ref(pmid, parameters):
    
    reflink = ReferenceLink(pmid, current_user.name.upper(), parameters)
    bad_names = reflink.invalid_names()
    if len(bad_names) > 0:
        return "Not found Gene name(s): " + ', '.join(bad_names)

    err = 0
                            
    try:
        message = reflink.insert_and_associate()
        db.session.commit()
    except:
        db.session.rollback()
        err = 1
        raise

    if err == 1:
        return "An error occurred when linking the reference for pmid = " + pmid + " to the info you picked/entered: " + parameters
    if message == None:
        return "Reference for pmid = " + pmid + " has been added into the database."
    return "Reference for pmid = " + pmid + " has been added into the database and associated with the following data:<p>" + message

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        error_code = Database.connect(username, password)
        if error_code:
            flash("You typed in an invalid username/password")
        else:    
            if username in USER_NAMES:
                remember = request.form.get("remember", "no") == "yes"
                if login_user(USER_NAMES[username], remember=remember):
                    flash("Logged in!")
                    return redirect(request.args.get("next") or url_for("index"))
                else:
                    flash("Sorry, but you could not log in.")
            else:
                flash("You are not allowed to use this interface. Contact sgd-programmers to add your name to the list.")
    return render_template("login.html")


@app.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
        confirm_login()
        flash(u"Reauthenticated.")
        # return redirect(request.args.get("next") or url_for("index"))
        return redirect(url_for("index"))
    return render_template("reauth.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    # db.session.close()
    # db.session.bind.dispose()
    flash("Logged out.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)    
