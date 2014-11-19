__author__ = 'kelley'

from datetime import datetime
import json
import logging
import uuid

from pyramid.response import Response
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func
from zope.sqlalchemy import ZopeTransactionExtension

from src.sgd.backend.backend_interface import BackendInterface
from src.sgd.go_enrichment import query_batter
from src.sgd.model import perf
from config import DBNAME, DBTYPE, PERF_DBHOST, PERF_DBPASS, PERF_DBUSER, PERF_SCHEMA

import cProfile
import StringIO
import pstats
import contextlib

@contextlib.contextmanager
def profiled():
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()
    s = StringIO.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
    ps.print_stats()
    # uncomment this to see who's calling what
    #ps.print_callers()
    print s.getvalue()[:1000]

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

if __name__ == '__main__':
    class Base(object):
        __table_args__ = {'schema': PERF_SCHEMA, 'extend_existing':True}

    perf.Base = declarative_base(cls=Base)

    engine = create_engine("%s://%s:%s@%s/%s" % (DBTYPE, PERF_DBUSER, PERF_DBPASS, PERF_DBHOST, DBNAME), convert_unicode=True, pool_recycle=3600)

    DBSession.configure(bind=engine)
    perf.Base.metadata.bind = engine

    from src.sgd.model.perf.core import Bioentity, Disambig
    query = DBSession.query(Disambig.obj_id).filter(Disambig.id == 2824569).first()
    start = datetime.now()
    with profiled():

        query = DBSession.query(Disambig.obj_id).filter(Disambig.disambig_key == 'ACT1').filter(Disambig.class_type=='BIOENTITY').filter(Disambig.subclass_type == 'LOCUS')
        #query = DBSession.query(Disambig.obj_id).filter(Disambig.id == 2824569)

        bioent_id = query.first().obj_id

        midway = datetime.now()
        print midway - start
        text = bioentity = DBSession.query(Bioentity).filter(Bioentity.id == bioent_id).first().json

    #if len(disambigs) > 0:
    #    print disambigs


    print datetime.now() - midway
    print text[:50]

