from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

source = 'SGD'
TAXON_ID = "TAX:4932"

def contignoteannotation_starter(bud_session_maker):

    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.contig import Contig
    from src.sgd.model.bud.sequence import Sequence, Seq_Change_Archive
    from src.sgd.model.bud.feature import Feature

    nex_session = get_nex_session()
    bud_session = bud_session_maker()

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)
    if taxonomy_id is None:
        print "The Taxon_id = ", TAXON_ID, " is not in the database"
        return
    bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    seq_change_archive_id_to_seq_id = dict([(x.id, x.sequence_id) for x in bud_session.query(Seq_Change_Archive).all()])
    seq_id_to_feature_id = dict([(x.id, x.feature_id) for x in bud_session.query(Sequence).all()])
    feature_id_to_name = dict([(x.id, x.name) for x in bud_session.query(Feature).all()])
    format_name_to_contig_id = dict([(x.format_name, x.id) for x in nex_session.query(Contig).all()])

    chrnum_to_roman = get_chr_to_roman_mapping()

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

    note_type = 'Chromosome'
    display_name = 'Sequence change'
    for x in bud_session.query(NoteFeat).all():
        
        if x.tab_name != 'SEQ_CHANGE_ARCHIVE':
            continue           
        seq_change_archive_id = x.primary_key
        seq_id = seq_change_archive_id_to_seq_id.get(seq_change_archive_id)
        if seq_id is None:
            print "The seq_change_archive_id: ", seq_change_archive_id, " is not in the SEQ_CHANGE_ARCHIVE table."
            continue
        feature_id = seq_id_to_feature_id.get(seq_id)
        if feature_id is None:
            print "The seq_id: ", seq_id, " is not in SEQ table."
            continue
        chr_num =feature_id_to_name.get(feature_id)
        if chr_num is None:
            print "The feature_no: ", feature_id, " is not in FEATURE table."
        chr_roman = chrnum_to_roman.get(chr_num)
        if chr_roman is None:
            print "The chrnum: ", chr_num, " can't be mapped to a roman numeral."
            continue
        format_name = "Chromosome_" + chr_roman
        contig_id = format_name_to_contig_id.get(format_name)
        if contig_id is None:
            print "The format_name: ", format_name, " is not in Contig table."
            continue
        data = { 'contig_id': contig_id,
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
   
def get_chr_to_roman_mapping():

    return { "1": "I",
             "2": "II",
             "3": "III",
             "4": "IV",
             "5": "V",
             "6": "VI",
             "7": "VII",
             "8": "VIII",
             "9": "IX",
             "10": "X",
             "11": "XI",
             "12": "XII",
             "13": "XIII",
             "14": "XIV",
             "15": "XV",
             "16": "XVI" }

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, contignoteannotation_starter, 'contignoteannotation', lambda x: (x['contig_id'], x['taxonomy_id'], x['note'], x['note_type'], x['display_name']))
