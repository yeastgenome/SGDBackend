from sqlalchemy import *
from src.sgd.convert import prepare_schema_connection
from src.sgd.convert import config
from src.sgd.model import nex

# TEST, get all the genes
def main():
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    from src.sgd.model.nex.bioentity import Bioentity
    nex_session = nex_session_maker()
    for bioent in nex_session.query(Bioentity).all():
        print bioent.format_name

main()
