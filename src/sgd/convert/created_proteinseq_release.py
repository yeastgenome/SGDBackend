from src.sgd.convert.util import prepare_schema_connection
from src.sgd.convert import config
from src.sgd.model import bud
from sqlalchemy.sql.expression import or_
from datetime import datetime

__author__ = 'sweng66'

def get_year_month_day(mydate):
    this_date = str(mydate).split(' ')[0].replace('-0', '-').split('-')
    return [int(this_date[0]), int(this_date[1]), int(this_date[2])]

def get_seq_version(seq_obj_list, release_year, release_month, release_day):
    seq_version = None
    residues = ''
    date_created = ''
    created_by = ''
    year = 0
    month = 0
    day = 0
    for x in seq_obj_list:
        [this_year, this_month, this_day] = get_year_month_day(x.seq_version)
        if datetime(this_year, this_month, this_day) > datetime(release_year, release_month, release_day):
            continue
        if seq_version is None or datetime(this_year, this_month, this_day) > datetime(year, month, day):
            seq_version = x.seq_version
            residues = x.residues
            date_created = x.date_created
            created_by = x.created_by
            year = this_year
            month = this_month
            day = this_day
    return [seq_version, residues, created_by, date_created]

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)

    from src.sgd.model.bud.feature import Feature, FeatRel
    from src.sgd.model.bud.sequence import Sequence, FeatLocation_Rel

    bud_session = bud_session_maker()
    
    feature_no_to_feature_obj = dict([(x.id, x) for x in bud_session.query(Feature).all()])

    feature_no_to_chr = {}
    for x in bud_session.query(FeatRel).filter_by(rank=1).all():
        feature_no_to_chr[x.child_id] = feature_no_to_feature_obj[x.parent_id].name
        
    feature_no_to_seq_obj = {}
    for x in bud_session.query(Sequence).filter_by(seq_type='protein').all():
        seq_obj = []
        if x.feature_id in feature_no_to_seq_obj:
            seq_obj = feature_no_to_seq_obj[x.feature_id]
        seq_obj.append(x)
        feature_no_to_seq_obj[x.feature_id] = seq_obj
    
    for x in bud_session.query(FeatLocation_Rel).all():
        feature_no = x.feature_location.feature_id
        feature_name = feature_no_to_feature_obj[feature_no].name
        gene_name = feature_no_to_feature_obj[feature_no].gene_name
        if gene_name is None:
            gene_name = ""
        version = x.release.genome_release
        chr = feature_no_to_chr.get(feature_no)
        if chr is None:
            continue
        seq_obj_list = feature_no_to_seq_obj.get(feature_no)
        if seq_obj_list is None:
            continue

        [release_year, release_month, release_day] = get_year_month_day(x.release.release_date)
   
        [seq_version, residues, created_by, date_created] = get_seq_version(seq_obj_list, 
                                                                            release_year,
                                                                            release_month,
                                                                            release_day)
          
        print version + "\t" + chr + "\t" + feature_name + "\t" + str(feature_no) + "\t" + gene_name + "\t" + str(seq_version) +"\t" + created_by + "\t" + str(date_created) + "\t" + str(residues) 

    bud_session.close()



