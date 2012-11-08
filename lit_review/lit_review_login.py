"""

This is a small application that provides a login page for curators to view/edit the
information in Oracle database. This application is using Flask-Login package (created
by Matthew Frazier, MIT) for handling the login sessions and everything. 

"""
from config import Anonymous, USER_NAMES, USERS
from flask_login import LoginManager, login_user, logout_user, confirm_login

login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

def setup_app(app):
    login_manager.setup_app(app)
        

def login_lit_review_user(username, remember):
    result = None
    if username in USER_NAMES:
        if login_user(USER_NAMES[username], remember=remember):
            result = LoginResult.SUCCESSFUL
        else:
            result = LoginResult.UNSUCCESSFUL
    else:
        result = LoginResult.NOT_ON_LIST
    return result

@login_manager.user_loader
def load_lit_review_user(user_id):
    return USERS.get(int(user_id))

def confirm_login_lit_review_user():
    confirm_login()
    return 'Reauthenticated'
    
def logout_lit_review_user():
    logout_user()
    return LogoutResult.SUCCESSFUL

class LoginResult:
    SUCCESSFUL=0
    NOT_ON_LIST=1
    UNSUCCESSFUL=2
    BAD_USERNAME_PASSWORD=3
    
class LogoutResult:
    SUCCESSFUL=0



    




