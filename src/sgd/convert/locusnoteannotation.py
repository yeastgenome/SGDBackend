from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

source = 'SGD'
TAXON_ID = "TAX:4932"

def locusnoteannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.sequence import Sequence, Feat_Location 

    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
    bud_id_to_dbentity_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    feat_loc_id_to_feature_id = dict([(x.id, x.feature_id) for x in bud_session.query(Feat_Location).all()])

    from src.sgd.model.bud.reference import Reflink
    
    note_id_to_reference_id = {}
    for x in bud_session.query(Reflink).filter_by(tab_name='NOTE').all():
        note_id = x.primary_key
        ref_bud_id = x.reference_id
        reference_id = bud_id_to_reference_id.get(ref_bud_id)
        if reference_id is None:
            print "The reference bud_id: ", ref_bud_id, " is not in the Reference table."
            continue
        note_id_to_reference_id[note_id] = reference_id

    from src.sgd.model.bud.general import NoteFeat

    note_types = annotation_note_types()

    for x in bud_session.query(NoteFeat).all():
        
        if x.tab_name not in ['FEATURE', 'FEAT_LOCATION']:
            continue

        note_type_key = x.note.note_type + ":" + x.tab_name 
        type_n_display_name = note_types.get(note_type_key)
        if type_n_display_name is None:
            continue
        
        (note_type, display_name) = type_n_display_name
           
        feature_id = None
        if x.tab_name == 'FEAT_LOCATION':
            feat_loc_id = x.primary_key
            feature_id = feat_loc_id_to_feature_id.get(feat_loc_id)
            if feature_id is None:
                print "The feat_location_id: ", feat_loc_id, " is not in the FEAT_LOCATION table."
                continue
        elif x.tab_name == 'FEATURE':
            feature_id = x.primary_key
        if feature_id is None:
            continue
        dbentity_id = bud_id_to_dbentity_id.get(feature_id)
        if dbentity_id is None:
            print "The BUD_ID: ", feature_id, " is not in the LOCUSDBENTITY table."
            continue

        data = { 'dbentity_id': dbentity_id,
                 'source': { "display_name": source },
                 'taxonomy_id': taxonomy_id,
                 'bud_id': x.id,
                 'note_type': note_type,
                 'display_name': display_name,
                 'note': x.note.note,
                 'date_created': str(x.date_created),
                 'created_by': x.created_by }

        reference_id = note_id_to_reference_id.get(x.note_id)
        if reference_id is not None:
            data['reference_id'] = reference_id

        yield data
        

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()
   
def annotation_note_types():
    
    return { "Alternative processing:FEATURE":  ("Sequence", "Alternative processing"),
             "Annotation change:FEATURE": ("Sequence", "Annotation change"),
             "Annotation change:FEAT_LOCATION": ("Sequence", "Annotation change"),
             "Curation note:FEATURE": ("Locus", "Locus history"),
             "Mapping:FEATURE": ("Sequence", "Mapping"),
             "Nomenclature conflict:FEATURE": ("Locus", "Nomenclature conflict"),
             "Nomenclature history:FEATURE": ("Locus", "Nomenclature history"),
             "Proposed annotation change:FEATURE": ("Sequence", "Proposed annotation change"),
             "Proposed sequence change:FEATURE": ("Sequence", "Proposed sequence change"),
             "Sequence change:FEATURE": ("Sequence", "Sequence change") }

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, locusnoteannotation_starter, 'locusnoteannotation', lambda x: (x['dbentity_id'], x['taxonomy_id'], x['note'], x['note_type'], x['display_name']))
