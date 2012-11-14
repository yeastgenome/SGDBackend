from flask_login import UserMixin, AnonymousUser
                             
HOST = '0.0.0.0'
PORT = 5000
SECRET_KEY = "SECRET_KEY_HERE"


DBTYPE = 'oracle'
DBHOST = 'SERVER:PORT'
DBNAME = 'DBNAME_HERE'
SCHEMA = 'SCHEMA_HERE'

class User(UserMixin):
    def __init__(self, name, user_id, active=True):
        self.name = name
        self.id = user_id
        self.active = active

    def is_active(self):
        return self.active

class Anonymous(AnonymousUser):
    name = u"Anonymous"

    
USERS = {
    1: User(u"maria", 1),
    2: User(u"john", 2),
    3: User(u"mary", 3),
    4: User(u"julie", 4),
    5: User(u"kpaskov", 5),
    6: User(u"otto", 6),
    7: User(u"guest", 7, False),
}

USER_NAMES = dict((u.name, u) for u in USERS.itervalues())



