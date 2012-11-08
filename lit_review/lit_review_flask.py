"""

This is a small application that provides a login page for curators to view/edit the
information in Oracle database. This application is using Flask-Login package (created
by Matthew Frazier, MIT) for handling the login sessions and everything. 

"""
from config import SECRET_KEY, HOST, PORT
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import login_required, fresh_login_required
from lit_review_login import LoginResult, LogoutResult, \
    confirm_login_lit_review_user, logout_lit_review_user, login_lit_review_user, \
    setup_app
from model_old_schema.db_connection import DBConnection

app = Flask(__name__)
conn = DBConnection()
setup_app(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reference")
@fresh_login_required
def reference():
    refs = conn.getRefTemps()
    num_of_refs = len(refs)
    return render_template('literature_review.html',
                           ref_list=refs,
                           ref_count=num_of_refs)    

@app.route("/reference/delete/<pmid>")
@fresh_login_required
def discard_ref(pmid):
    moved = conn.moveRefTempToRefBad(pmid)
    if moved:
        return "Reference for pmid=" + pmid + " has been removed from the database!"
    else:
        return "An error occurred when deleting the reference for pmid=" + pmid + " from the database."


@app.route("/reference/link/<pmid>/<parameters>")
@fresh_login_required
def link_ref(pmid, parameters):
    
#    reflink = ReferenceLink(pmid, current_user.name.upper(), parameters)
#    bad_names = reflink.invalid_names()
#    if len(bad_names) > 0:
#        return "Not found Gene name(s): " + ', '.join(bad_names)
#
#    err = 0
#                            
#    try:
#        message = reflink.insert_and_associate()
#        db.session.commit() #@UndefinedVariable
#    except:
#        db.session.rollback() #@UndefinedVariable
#        err = 1
#        raise
#
#    if err == 1:
#        return "An error occurred when linking the reference for pmid = " + pmid + " to the info you picked/entered: " + parameters
#    if message == None:
#        return "Reference for pmid = " + pmid + " has been added into the database."
#    return "Reference for pmid = " + pmid + " has been added into the database and associated with the following data:<p>" + message
    "return link_ref()"

@app.route("/login", methods=["GET", "POST"])
def login():
    result = None
    if request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        remember = request.form.get("remember", "no") == "yes"
        conn.connect(username, password)
        
        if conn.isConnected():
            result = login_lit_review_user(username, remember)
        else:
            result = LoginResult.BAD_USERNAME_PASSWORD
            
        output = {
            LoginResult.SUCCESSFUL: "Logged in!",
            LoginResult.NOT_ON_LIST: "You are not allowed to use this interface. Contact sgd-programmers to add your name to the list.",
            LoginResult.UNSUCCESSFUL: "Sorry, but you could not log in.",
            LoginResult.BAD_USERNAME_PASSWORD: "You typed in an invalid username/password"
        }[result]
        flash(output)
        
    if result == LoginResult.SUCCESSFUL:
        return redirect(request.args.get("next") or url_for("index"))
    else:
        return render_template("login.html")


@app.route("/reauth", methods=["GET", "POST"])
@login_required
def reauth():
    if request.method == "POST":
        output = confirm_login_lit_review_user()
        flash(output)
        return redirect(url_for("index"))
    return render_template("reauth.html")


@app.route("/logout")
@login_required
def logout():
    result = logout_lit_review_user()
    output = {
        LogoutResult.SUCCESSFUL: 'Logged out.'
    }[result]
    flash(output)
    return redirect(url_for("index"))




if __name__ == "__main__":
    app.secret_key = SECRET_KEY
    app.run(host=HOST, port=PORT, debug=True) 