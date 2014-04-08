import logging

from sqlalchemy.sql.expression import or_

from src.sgd.convert import create_format_name
from src.sgd.convert.transformers import TransformerInterface, make_multi_starter, make_db_starter, \
    make_file_starter


__author__ = 'kpaskov'

#--------------------- Convert Orphans ---------------------
def make_orphan_starter(bud_session):
    from src.sgd.model.bud.phenotype import ExperimentProperty
    from src.sgd.model.bud.go import GorefDbxref
    return make_multi_starter([make_db_starter(bud_session.query(ExperimentProperty).filter(ExperimentProperty.type == 'Reporter'), 1000),
                               make_db_starter(bud_session.query(GorefDbxref), 1000)])

class BudObj2OrphanObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioitem import Orphanbioitem
        from src.sgd.model.bud.phenotype import ExperimentProperty
        from src.sgd.model.bud.go import GorefDbxref

        if isinstance(bud_obj, ExperimentProperty):
            if bud_obj.type == 'Reporter':
                return Orphanbioitem(bud_obj.value, None, self.key_to_source['SGD'], None, None)
        elif isinstance(bud_obj, GorefDbxref):
            dbxref = bud_obj.dbxref
            dbxref_type = dbxref.dbxref_type
            if dbxref_type != 'GOID' and dbxref_type != 'EC number' and dbxref_type != 'DBID Primary' and dbxref_type != 'PANTHER' and dbxref_type != 'Prosite':
                source_key = create_format_name(dbxref.source)
                source = None if source_key not in self.key_to_source else self.key_to_source[source_key]
                if source is None:
                    print 'Source not found: ' + str(source_key)
                    return None
                link = None
                bioitem_type = None
                if dbxref_type == 'UniProt/Swiss-Prot ID':
                    urls = dbxref.urls
                    if len(urls) == 1:
                        link = urls[0].url.replace('_SUBSTITUTE_THIS_', dbxref.dbxref_id)
                    bioitem_type = 'UniProtKB'
                elif dbxref_type == 'UniProtKB Subcellular Location':
                    link = "http://www.uniprot.org/locations/" + dbxref.dbxref_id
                    bioitem_type = 'UniProtKB-SubCell'
                elif dbxref_type == 'InterPro':
                    link = "http://www.ebi.ac.uk/interpro/entry/" + dbxref.dbxref_id
                    bioitem_type = 'InterPro'
                elif dbxref_type == 'DNA accession ID':
                    link = None
                    bioitem_type = 'EMBL'
                elif dbxref_type == 'Gene ID':
                    link = None
                    bioitem_type = dbxref.source
                elif dbxref_type == 'HAMAP ID' or dbxref_type == 'HAMAP':
                    link = None
                    bioitem_type = 'HAMAP'
                elif dbxref_type == 'PDB identifier':
                    link = None
                    bioitem_type = 'PDB'
                elif dbxref_type == 'Protein version ID':
                    link = None
                    bioitem_type = 'protein_id'
                elif dbxref_type == 'UniPathway ID':
                    link = 'http://www.grenoble.prabi.fr/obiwarehouse/unipathway/upa?upid=' + dbxref.dbxref_id
                    bioitem_type = 'UniPathway'
                elif dbxref_type == 'UniProtKB Keyword':
                    link = 'http://www.uniprot.org/keywords/' + dbxref.dbxref_id
                    bioitem_type = 'UniProtKB-KW'
                return Orphanbioitem(dbxref.dbxref_id, link, source, dbxref.dbxref_name, bioitem_type)
        return None

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

#--------------------- Convert Allele ---------------------
def make_allele_starter(bud_session):
    from src.sgd.model.bud.phenotype import ExperimentProperty
    return make_db_starter(bud_session.query(ExperimentProperty).filter(ExperimentProperty.type == 'Allele'), 1000)

class BudObj2AlleleObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioitem import Allele

        if bud_obj.type == 'Allele':
            return Allele(bud_obj.value, self.key_to_source['SGD'], None)
        return None

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

# --------------------- Convert Domain ---------------------
def make_domain_starter(bud_session):
    from src.sgd.model.bud.sequence import ProteinDetail
    from src.sgd.model.bud.general import Dbxref
    return make_multi_starter([make_file_starter('src/sgd/convert/data/yeastmine_protein_domains.tsv'),
                               make_file_starter('src/sgd/convert/data/TF_family_class_accession04302013.txt'),
                               make_db_starter(bud_session.query(ProteinDetail), 1000),
                               make_db_starter(bud_session.query(Dbxref).filter(or_(Dbxref.dbxref_type == 'PANTHER', Dbxref.dbxref_type == 'Prosite')), 1000)])

class BudObj2DomainObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioitem import Domain
        from src.sgd.model.bud.sequence import ProteinDetail
        from src.sgd.model.bud.general import Dbxref

        if isinstance(bud_obj, list):
            if len(bud_obj) > 10:
                source_key = bud_obj[13].strip()

                display_name = bud_obj[3].strip()
                description = bud_obj[4].strip()
                interpro_id = bud_obj[5].strip()
                interpro_description = bud_obj[6].strip()

                #Need to check these links
                if source_key == 'JASPAR':
                    link = 'http://jaspar.binf.ku.dk/cgi-bin/jaspar_db.pl?rm=present&collection=CORE&ID=' + display_name
                elif source_key == 'HMMSmart':
                    source_key = 'SMART'
                    link = "http://smart.embl-heidelberg.de/smart/do_annotation.pl?DOMAIN=" + display_name
                elif source_key == 'HMMPfam':
                    source_key = 'Pfam'
                    link = "http://pfam.sanger.ac.uk/family?type=Family&entry=" + display_name
                elif source_key == 'Gene3D':
                    link = "http://www.cathdb.info/version/latest/superfamily/" + display_name[6:]
                elif source_key == 'superfamily':
                    source_key = 'SUPERFAMILY'
                    link = "http://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid=" + display_name
                elif source_key == 'Seg':
                    source_key = '-'
                    link = None
                elif source_key == 'Coil':
                    source_key = '-'
                    link = None
                elif source_key == 'HMMPanther':
                    source_key = 'PANTHER'
                    link = "http://www.pantherdb.org/panther/family.do?clsAccession=" + display_name
                elif source_key == 'HMMTigr':
                    source_key = 'TIGRFAMs'
                    link = "http://cmr.tigr.org/tigr-scripts/CMR/HmmReport.cgi?hmm_acc=" + display_name
                elif source_key == 'FPrintScan':
                    source_key = 'PRINTS'
                    link = "http:////www.bioinf.man.ac.uk/cgi-bin/dbbrowser/sprint/searchprintss.cgi?display_opts=Prints&amp;category=None&amp;queryform=false&amp;prints_accn=" + display_name
                elif source_key == 'BlastProDom':
                    source_key = 'ProDom'
                    link = "http://prodom.prabi.fr/prodom/current/cgi-bin/request.pl?question=DBEN&amp;query=" + display_name
                elif source_key == 'HMMPIR':
                    source_key = "PIR superfamily"
                    link = "http://pir.georgetown.edu/cgi-bin/ipcSF?" + display_name
                elif source_key == 'ProfileScan':
                    source_key = 'PROSITE'
                    link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
                elif source_key == 'PatternScan':
                    source_key = 'PROSITE'
                    link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
                else:
                    print 'No link for source = ' + source_key + ' ' + str(display_name)
                    return None

                source_key = create_format_name(source_key)
                source = None if source_key not in self.key_to_source else self.key_to_source[source_key]

                description = None if description == 'no description' else description
                interpro_description = None if interpro_description == 'NULL' else interpro_description
                interpro_id = None if interpro_id == 'NULL' else interpro_id

                return Domain(display_name, source, description if description is not None else interpro_description, interpro_id, source_key, interpro_description, link)
            else:
                display_name = bud_obj[0]
                description = 'Class: ' + bud_obj[4] + ', Family: ' + bud_obj[3]
                interpro_id = None
                interpro_description = None

                link = 'http://jaspar.binf.ku.dk/cgi-bin/jaspar_db.pl?rm=present&collection=CORE&ID=' + display_name

                return Domain(display_name, self.key_to_source['JASPAR'], description if description is not None else interpro_description, 'JASPAR', interpro_id, interpro_description, link)
        elif isinstance(bud_obj, ProteinDetail):
            if bud_obj.type == 'signal peptide':
                return Domain('predicted signal peptide', self.key_to_source['SignalP'], 'predicted signal peptide', 'SignalP', None, None, None)
            elif bud_obj.type == 'predicted transmembrane domain':
                return Domain('predicted transmembrane domain', self.key_to_source['TMHMM'], 'predicted transmembrane domain', 'TMHMM', None, None, None)
        elif isinstance(bud_obj, Dbxref):
            dbxref_type = bud_obj.dbxref_type
            source_key = create_format_name(bud_obj.source)
            source = None if source_key not in self.key_to_source else self.key_to_source[source_key]
            if source is None:
                print source_key
                return []
            link = None
            bioitem_type = None
            if dbxref_type == 'Prosite ID':
                bioitem_type = 'Prosite'
                link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + bud_obj.dbxref_id
            elif dbxref_type == 'PANTHER':
                bioitem_type = 'PANTHER'
                link = "http://www.pantherdb.org/panther/family.do?clsAccession=" + bud_obj.dbxref_id
            return Domain(bud_obj.dbxref_id, source, bud_obj.dbxref_name, bioitem_type, None, None, link)

        return None

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

#1.23.14 Maitenance (sgd-dev): :19

# --------------------- Convert Chemical ---------------------
def make_chemical_starter(bud_session):
    from src.sgd.model.bud.cv import CVTerm
    from src.sgd.model.bud.phenotype import ExperimentProperty
    return make_multi_starter([make_db_starter(bud_session.query(ExperimentProperty).filter(or_(ExperimentProperty.type=='Chemical_pending', ExperimentProperty.type == 'chebi_ontology')), 1000),
                               make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no == 3), 1000)])

class BudObj2ChemicalObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioitem import Chemical
        from src.sgd.model.bud.phenotype import ExperimentProperty
        from src.sgd.model.bud.cv import CVTerm

        if isinstance(bud_obj, ExperimentProperty):
            display_name = bud_obj.value
            source = self.key_to_source['SGD']
            return Chemical(display_name, source, None, None, bud_obj.date_created, bud_obj.created_by)
        elif isinstance(bud_obj, CVTerm):
            source = self.key_to_source['SGD']
            return Chemical(bud_obj.name, source, bud_obj.dbxref_id,
                                       bud_obj.definition, bud_obj.date_created, bud_obj.created_by)
        return None

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

# --------------------- Convert Contig ---------------------
class BudObj2ContigObj(TransformerInterface):

    def __init__(self, session_maker):
        self.session = session_maker()

        from src.sgd.model.nex.misc import Source
        self.key_to_source = dict([(x.unique_key(), x) for x in self.session.query(Source).all()])

    def convert(self, bud_obj):
        from src.sgd.model.nex.bioitem import Contig
        display_name, residues, strain = bud_obj
        source = self.key_to_source['SGD']
        return Contig(display_name, source, residues, strain)

    def finished(self, delete_untouched=False, commit=False):
        self.session.close()
        return None

def create_contig(sequence_library, strain, source):
    from src.sgd.model.nex.bioitem import Contig
    return [Contig(x, source, y, strain) for x, y in sequence_library.iteritems()]

def convert_strain_contig(filename, strain, key_to_source, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids):
    #Grab old objects
    f = open(filename, 'r')
    sequence_library = get_dna_sequence_library(f)
    f.close()

    source = key_to_source['SGD']
    newly_created_objs = create_contig(sequence_library, strain, source)

    if newly_created_objs is not None:
        #Edit or add new objects
        for newly_created_obj in newly_created_objs:
            unique_key = newly_created_obj.unique_key()
            if unique_key not in already_seen:
                current_obj_by_id = None if newly_created_obj.id not in id_to_current_obj else id_to_current_obj[newly_created_obj.id]
                current_obj_by_key = None if unique_key not in key_to_current_obj else key_to_current_obj[unique_key]
                create_or_update(newly_created_obj, current_obj_by_id, current_obj_by_key, values_to_check, new_session, output_creator)

                if current_obj_by_id is not None and current_obj_by_id.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_id.id)
                if current_obj_by_key is not None and current_obj_by_key.id in untouched_obj_ids:
                    untouched_obj_ids.remove(current_obj_by_key.id)

                already_seen.add(unique_key)

    output_creator.finished()
    new_session.commit()

def convert_contig(new_session_maker):
    from src.sgd.model.nex.bioitem import Contig
    from src.sgd.model.nex.misc import Strain, Source

    new_session = None
    log = logging.getLogger('convert.sequence.contig')
    output_creator = OutputCreator(log)

    try:
        new_session = new_session_maker()

        #Values to check
        values_to_check = ['display_name', 'residues', 'link']

        #Grab current objects
        current_objs = new_session.query(Contig).all()
        id_to_current_obj = dict([(x.id, x) for x in current_objs])
        key_to_current_obj = dict([(x.unique_key(), x) for x in current_objs])

        key_to_strain = dict([(x.unique_key(), x) for x in new_session.query(Strain).all()])
        key_to_source = dict([(x.unique_key(), x) for x in new_session.query(Source).all()])

        untouched_obj_ids = set(id_to_current_obj.keys())
        already_seen = set()

        for filename, strain in sequence_files:
            convert_strain_contig(filename, key_to_strain[strain.replace('.', '')], key_to_source, values_to_check, new_session, output_creator, id_to_current_obj, key_to_current_obj, already_seen, untouched_obj_ids)

        #Delete untouched objs
        for untouched_obj_id in untouched_obj_ids:
            new_session.delete(id_to_current_obj[untouched_obj_id])
            output_creator.removed()

        #Commit
        output_creator.finished()
        new_session.commit()

    except Exception:
        log.exception('Unexpected error:' + str(sys.exc_info()[0]))
    finally:
        new_session.close()
