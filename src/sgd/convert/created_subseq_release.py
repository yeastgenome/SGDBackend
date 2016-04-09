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

def get_coord_version(feat_loc_obj_list, release_year, release_month, release_day):
    coord_version = None
    min_coord = 0
    max_coord = 0
    year = 0
    month = 0
    day = 0
    for x in feat_loc_obj_list:
        [this_year, this_month, this_day] = get_year_month_day(x.coord_version)
        if datetime(this_year, this_month, this_day) > datetime(release_year, release_month, release_day):
            continue
        if coord_version is None or datetime(this_year, this_month, this_day) > datetime(year, month, day):
            coord_version = x.coord_version
            min_coord = x.min_coord
            max_coord = x.max_coord
            year = this_year
            month = this_month
            day = this_day
    return [coord_version, min_coord, max_coord]

if __name__ == "__main__":

    bud_session_maker = prepare_schema_connection(bud, config.BUD_DBTYPE, 'pastry.stanford.edu:1521', config.BUD_DBNAME, config.BUD_SCHEMA, config.BUD_DBUSER, config.BUD_DBPASS)

    from src.sgd.model.bud.feature import Feature, FeatRel
    from src.sgd.model.bud.sequence import Sequence, Feat_Location, FeatLocation_Rel

    bud_session = bud_session_maker()
    
    # %featureNo2featureObj
    feature_no_to_feature_obj = dict([(x.id, x) for x in bud_session.query(Feature).all()])
    
    # %seqNo2seqObj
    seq_no_to_seq_obj = dict([(x.id, x) for x in bud_session.query(Sequence).all()])
    
    # %parentFeatNo2subFeatNoList
    feature_no_to_subfeat_no_list = {}
    for x in bud_session.query(FeatRel).filter(or_(FeatRel.rank==2 , FeatRel.rank==4)).all():
        ids = []
        if x.parent_id in feature_no_to_subfeat_no_list:
            ids = feature_no_to_subfeat_no_list[x.parent_id]
        ids.append(x.child_id)
        feature_no_to_subfeat_no_list[x.parent_id] = ids

    # %featureNo2chr
    feature_no_to_chr = {}
    for x in bud_session.query(FeatRel).filter_by(rank=1).all():
        feature_no_to_chr[x.child_id] = feature_no_to_feature_obj[x.parent_id].name
        
    feature_no_to_seq_obj = {}
    for x in bud_session.query(Sequence).filter_by(seq_type='genomic').all():
        seq_obj = []
        if x.feature_id in feature_no_to_seq_obj:
            seq_obj = feature_no_to_seq_obj[x.feature_id]
        seq_obj.append(x)
        feature_no_to_seq_obj[x.feature_id] = seq_obj
    
    feature_no_to_feat_loc_obj = {}
    for x in bud_session.query(Feat_Location).all():
        feat_loc_obj = []
        if x.feature_id in feature_no_to_feat_loc_obj:
            feat_loc_obj = feature_no_to_feat_loc_obj[x.feature_id]
        feat_loc_obj.append(x)
        feature_no_to_feat_loc_obj[x.feature_id] = feat_loc_obj
        
    for x in bud_session.query(FeatLocation_Rel).all():
        # parent info 
        parent_feature_no = x.feature_location.feature_id
        parent_feature_name = feature_no_to_feature_obj[parent_feature_no].name
        parent_gene_name = feature_no_to_feature_obj[parent_feature_no].gene_name
        if parent_gene_name is None:
            parent_gene_name = ""
        version = x.release.genome_release
        chr = feature_no_to_chr.get(parent_feature_no)
        if chr is None:
            continue
        
        # subfeature info
        if parent_feature_no not in feature_no_to_subfeat_no_list:
            continue
        for child_feature_no in feature_no_to_subfeat_no_list[parent_feature_no]:
            child_feature_name = feature_no_to_feature_obj[child_feature_no].name
            child_feature_type = feature_no_to_feature_obj[child_feature_no].type
            [release_year, release_month, release_day] = get_year_month_day(x.release.release_date)
            if child_feature_no not in feature_no_to_seq_obj:
                print "The subfeature: feature_no = ", child_feature_no, " is not in seq table."
                continue
            [child_seq_version, residues, created_by, date_created] = get_seq_version(feature_no_to_seq_obj[child_feature_no], 
                                                                                      release_year,
                                                                                      release_month,
                                                                                      release_day)
            if child_feature_no not in feature_no_to_feat_loc_obj:
                print "The subfeature: feature_no = ", child_feature_no, " is not in feat_location table."
                continue
            [child_coord_version, min_coord, max_coord] = get_coord_version(feature_no_to_feat_loc_obj[child_feature_no], 
                                                                            release_year, 
                                                                            release_month, 
                                                                            release_day)

            print version + "\t" + chr + "\t" + parent_feature_name + "\t" + str(parent_feature_no) + "\t" + parent_gene_name + "\t" + child_feature_name + "\t" + str(child_feature_no) + "\t" + child_feature_type + "\t" + str(child_seq_version) + "\t" + str(child_coord_version) + "\t" + str(min_coord) + "\t" + str(max_coord) + "\t" + created_by + "\t" + str(date_created) + "\t" + str(residues) 

 
    bud_session.close()



