'''
Created on Nov 5, 2012

@author: kpaskov
'''
from connection_test.config import DBTYPE, DBHOST, DBNAME, DBUSER, DBPASS, \
    SCHEMA
from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import Table

app = Flask(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME)
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600


db = SQLAlchemy(app)
db(bind = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, DBUSER, DBPASS, DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600))
metadata = db.MetaData(bind=db.engine)

class Feature(db.Model):
    __table__ = Table('feature', metadata, autoload = True, schema = SCHEMA)

    #Values
    id = __table__.c.feature_no
    name = __table__.c.feature_name
    type = __table__.c.feature_type
    source = __table__.c.source
    status = __table__.c.status
    gene_name = __table__.c.gene_name

class Test():
    def getFirstFeature(self):
        #Get the first Feature.
        session = db.session;
        return session.query(Feature).first()
    
    
if __name__ == "__main__":
    print Test().getFirstFeature().name