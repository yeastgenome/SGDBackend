from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

source = 'SGD'
TAXON_ID = "TAX:4932"

def locusnoteannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.sequence import Sequence, Feat_Location
    from src.sgd.model.bud.reference import Reflink, Reference as Reference_bud
    from src.sgd.model.bud.feature import Feature

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
    feat_alias_no_to_reference_no = dict([(int(x.primary_key), x.reference_id) for x in bud_session.query(Reflink).filter_by(tab_name='FEAT_ALIAS').all()])
    

    ######### START
    # load the "notes" about when a gene name was assigned.                 
    # A date associated with every gene_name and alias for an ORF                                    
    # should be displayed in the 'History' section on the LSP.                                        
    # BUD.ARCHIVE where archive_type = 'Gene name'                                                    
    # From BUD.REF_LINK where tab_name = 'FEATURE' and col_name = 'GENE_NAME'                         
    # get the REFERENCE_NO and then use REFERENCE.DATE_PUBLISHED for any gene                         
    # name that is not in the ARCHIVE table.                                                          
    # display_name = 'Nomenclature' and "note" format = Name: [Gene name]   

    from datetime import datetime

    mon_to_number = { "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,  "May": 5,  "Jun": 6,
                      "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12 }

    reference_no_to_date_published = {}
    reference_no_to_year = {}
    for x in bud_session.query(Reference_bud).all():        
        reference_no_to_date_published[x.id] = x.date_published
        reference_no_to_year[x.id] = x.year

    feature_no_to_reference_no = {}
    feature_no_to_date_published = {}
    for x in bud_session.query(Reflink).filter_by(tab_name='FEATURE').filter_by(col_name='GENE_NAME').all():
        feature_no_to_reference_no[x.primary_key] = x.reference_id
        date_published = reference_no_to_date_published[x.reference_id]
        this_year = reference_no_to_year[x.reference_id]
        if date_published and ' ' in date_published: 
            date_list = date_published.split(' ')
            year = int(date_list[0])
            ## sometimes mon = 'Jul-Aug'
            mon = date_list[1]
            if "-" in mon:
                mon = date_list[1].split('-')[1]
            ## sometimes mon = 'July'
            mon = mon[0:3]
            month = 1
            if mon_to_number.get(mon) is not None:                                                                                 
                month = int(mon_to_number[mon]) 
            if len(date_list) > 2:
                if ',' in date_list[2]:  
                    date_list[2] = date_list[2].replace(',', '-')
                if '-' in date_list[2]: 
                    days = date_list[2].split('-') 
                    if days[0]: 
                        day = int(days[0])
                    elif days[1]:
                        day = int(days[1]) 
                    else:
                        day = 1
                else:
                    day = int(date_list[2])
            else:
                day = 1

            feature_no_to_date_published[x.primary_key] = datetime(year, month, day)
        else:
            feature_no_to_date_published[x.primary_key] = datetime(this_year, 1, 1) 

    from src.sgd.model.bud.feature import Archive

    key_to_archive_row = dict([((x.feature_id, x.new_value), x) for x in bud_session.query(Archive).filter_by(archive_type='Gene name').all()])

    for x in bud_session.query(Feature).all():
        if x.gene_name is None:
            continue

        ## handle standard gene name here

        key = (x.id, x.gene_name)
        archive_row = key_to_archive_row.get(key)
        date_created = None
        if archive_row is not None:
            date_created = archive_row.date_created
        if date_created is None:
            date_created = feature_no_to_date_published.get(x.id)
            if date_created is not None:
                date_created = str(date_created).split(' ')[0]
        if date_created is None:
            continue

        dbentity_id = bud_id_to_dbentity_id.get(x.id)
        if dbentity_id is None:
            print "The BUD_ID: ", x.id, " is not in the LOCUSDBENTITY table."
            continue

        data = { 'dbentity_id': dbentity_id,
                 'source': { "display_name": source },
                 'taxonomy_id': taxonomy_id,
                 'bud_id': x.id,
                 'note_type': 'Locus',
                 'display_name': "Nomenclature",
                 'note': "Name: " + x.gene_name,
                 'date_created': str(date_created),
                 'created_by': x.created_by }

        reference_no = feature_no_to_reference_no.get(x.id)
        if reference_no is not None:
            reference_id = bud_id_to_reference_id.get(reference_no)
            if reference_id is not None:
                data['reference_id'] = reference_id

        yield data

        ### handle alias names 

        # feat_aliases = x.aliases
        for y in x.aliases:
            key = (x.id, y.alias_name)
            archive_row = key_to_archive_row.get(key)
            if archive_row is None:
                continue
            date_created = archive_row.date_created
            data2 = { 'dbentity_id': dbentity_id,
                      'source': { "display_name": source },
                      'taxonomy_id': taxonomy_id,
                      'note_type': 'Locus',
                      'display_name': "Nomenclature",
                      'note': "Name: " + y.alias_name,
                      'date_created': str(date_created),
                      'created_by': x.created_by }
            reference_no = feat_alias_no_to_reference_no.get(y.id)
            if reference_no is None:
                print "No reference_no for feat_alias_no=", y.id
                yield data2
                continue
            reference_id = bud_id_to_reference_id.get(reference_no)
            if reference_id is None:
                print "The reference_no: ", reference_no, " is not in REFERENCEDBENTITY table."
                yield data2
            else:
                data2['reference_id'] = reference_id
                yield data2
            
    ######### END
    
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
