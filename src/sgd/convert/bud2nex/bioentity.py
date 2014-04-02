from sqlalchemy.orm import joinedload

from src.sgd.convert import break_up_file
from src.sgd.convert.transformers import TransformerInterface, make_db_starter, make_file_starter


__author__ = 'kpaskov'

#Recorded times: 
#Maitenance (cherry-vm08): 2:56, 2:59 
#First Load (sgd-ng1): 4:08, 3:49
#Maitenance (sgd-ng1): 4:17
#1.23.14 Maitenance (sgd-dev): :27

# --------------------- Convert Locus ---------------------
def make_locus_starter(bud_session):
    from src.sgd.model.bud.feature import Feature
    return make_db_starter(bud_session.query(Feature).options(joinedload('annotation')), 1000)

class BudObj2LocusObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

        self.sgdid_to_uniprotid = {}
        for line in break_up_file('src/sgd/convert/data/YEAST_559292_idmapping.dat'):
            if line[1].strip() == 'SGD':
                self.sgdid_to_uniprotid[line[2].strip()] = line[0].strip()

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioentity import Locus

        display_name = bud_obj.gene_name
        if display_name is None:
            display_name = bud_obj.name

        format_name = bud_obj.name

        name_description = None
        headline = None
        description = None

        ann = bud_obj.annotation
        if ann is not None:
            name_description = ann.name_description
            headline = ann.headline
            description = ann.description

        sgdid = bud_obj.dbxref_id
        uniprotid = None if sgdid not in self.sgdid_to_uniprotid else self.sgdid_to_uniprotid[sgdid]

        source_key = bud_obj.source
        source = None if source_key not in self.key_to_source else self.key_to_source[source_key]
        bioentity = Locus(bud_obj.id, display_name, format_name, source, sgdid, uniprotid, bud_obj.status,
                             bud_obj.type, name_description, headline, description, bud_obj.gene_name,
                             bud_obj.date_created, bud_obj.created_by)
        return bioentity

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

# --------------------- Convert Transcript ---------------------
class BudObj2TranscriptObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        from src.sgd.model.nex.bioentity import Bioentity
        self.id_to_bioentity = dict([(x.id, x) for x in self.session.query(Bioentity).all()])
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioentity import Transcript

        locus_id = bud_obj.feature_id
        if locus_id not in self.id_to_bioentity:
            print 'Bioentity does not exist. ' + str(locus_id)
            return None
        locus = None if locus_id not in self.id_to_bioentity else self.id_to_bioentity[locus_id]
        source = self.key_to_source['SGD']
        return Transcript(None, source, locus, bud_obj.date_created, bud_obj.created_by)

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None
    
# --------------------- Convert Protein ---------------------
class BudObj2ProteinObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        from src.sgd.model.nex.bioentity import Bioentity
        self.id_to_bioentity = dict([(x.id, x) for x in self.session.query(Bioentity).all()])
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioentity import Protein

        locus_id = bud_obj.feature_id
        if locus_id not in self.id_to_bioentity:
            print 'Bioentity does not exist. ' + str(locus_id)
            return None
        locus = None if locus_id not in self.id_to_bioentity else self.id_to_bioentity[locus_id]
        source = self.key_to_source['SGD']
        return Protein(None, source, locus, bud_obj.date_created, bud_obj.created_by)

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

#--------------------- Convert Complex ---------------------
def make_complex_starter():
    return make_file_starter('src/sgd/convert/data/go_complexes.txt', offset=2)

class BudObj2ComplexObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        from src.sgd.model.nex.bioconcept import Go
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])
        self.key_to_go = dict([(x.unique_key(), x) for x in self.session.query(Go).all()])

    def convert(self, row):
        from src.sgd.model.nex.bioentity import Complex

        go_key = (row[2], 'GO')
        go = None if go_key not in self.key_to_go else self.key_to_go[go_key]
        if go is None:
            print 'Go not found: ' + str(go_key)
            return None

        source = self.key_to_source['SGD']
        return Complex(None, source, None, go, row[3])

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None