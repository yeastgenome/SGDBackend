'''
Created on Oct 18, 2012

@author: kpaskov
'''

from config import SECRET_KEY, HOST, PORT
from connection_test.config import USER_NAMES, Anonymous, USERS
from connection_test.db_connection import DBConnection
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, logout_user, confirm_login, \
    fresh_login_required, login_user, current_user
from reference.literature import ReferenceLink

db_connection = DBConnection("OTTO", "db4auto");

app = Flask(__name__)
app.config.from_object(__name__)

login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(user_id):
    return USERS.get(int(user_id))

login_manager.setup_app(app)

   
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        
        global db_connection;
        db_connection = DBConnection(username, password);
        
        if not db_connection.isConnect():
            flash("You typed in an invalid username/password")
        else:    
            if username in USER_NAMES:
                remember = True
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
        return redirect(url_for("index"))
    return render_template("reauth.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))

@app.route("/reference")
@fresh_login_required
def reference():
    refs = db_connection.getRefTemps();
    return render_template('literature_review.html',
                           ref_list=refs,
                           ref_count= len(refs))

@app.route("/reference/delete/<pmid>")
@fresh_login_required
def discard_ref(pmid):
    if(db_connection.discardRef(pmid)):
        return "Reference for pmid=" + pmid + " has been removed from the database!"
    else:
        return "An error occurred when deleting the reference for pmid=" + pmid + " from the database."

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
    except:
        err = 1
        raise

    if err == 1:
        return "An error occurred when linking the reference for pmid = " + pmid + " to the info you picked/entered: " + parameters
    if message == None:
        return "Reference for pmid = " + pmid + " has been added into the database."
    return "Reference for pmid = " + pmid + " has been added into the database and associated with the following data:<p>" + message

if __name__ == "__main__":
    app.secret_key = SECRET_KEY
    app.run(host=HOST, port=PORT, debug=True) 

    