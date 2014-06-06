from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import joinedload

from src.sgd.convert import create_format_name
from src.sgd.convert.transformers import make_db_starter, \
    make_file_starter, make_fasta_file_starter


__author__ = 'kpaskov'

#--------------------- Convert Orphans ---------------------
def make_orphan_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.phenotype import ExperimentProperty
    from src.sgd.model.bud.go import GorefDbxref

    def orphan_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_db_starter(bud_session.query(ExperimentProperty).filter(ExperimentProperty.type == 'Reporter'), 1000)():
            if bud_obj.type == 'Reporter':
                yield {'display_name': bud_obj.value,
                       'source': key_to_source['SGD']}

        for bud_obj in make_db_starter(bud_session.query(GorefDbxref), 1000)():
            dbxref = bud_obj.dbxref
            dbxref_type = dbxref.dbxref_type
            if dbxref_type != 'GOID' and dbxref_type != 'EC number' and dbxref_type != 'DBID Primary' and dbxref_type != 'PANTHER' and dbxref_type != 'Prosite':
                source_key = create_format_name(dbxref.source)
                source = None if source_key not in key_to_source else key_to_source[source_key]
                if source is None:
                    print 'Source not found: ' + str(source_key)
                    yield None
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
                yield {'display_name': dbxref.dbxref_id,
                       'link': link,
                       'source': source,
                       'description': dbxref.dbxref_name,
                      'bioitem_type': bioitem_type}
        bud_session.close()
        nex_session.close()

    return orphan_starter

#--------------------- Convert Allele ---------------------
def make_allele_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.phenotype import ExperimentProperty

    def allele_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_db_starter(bud_session.query(ExperimentProperty).filter(ExperimentProperty.type == 'Allele'), 1000)():
            if bud_obj.type == 'Allele':
                yield {'display_name': bud_obj.value,
                       'source': key_to_source['SGD']}

        bud_session.close()
        nex_session.close()
    return allele_starter

# --------------------- Convert Domain ---------------------
def make_domain_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.general import Dbxref

    def domain_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        panther_id_to_description = {}
        for row in make_file_starter('src/sgd/convert/data/PANTHER9.0_HMM_classifications.txt')():
            panther_id_to_description[row[0]] = row[1].lower()

        not_a_panther_id = set()
        for row in make_file_starter('src/sgd/convert/data/yeastmine_protein_domains.tsv')():
            source_key = row[10].strip()

            display_name = row[3].strip()
            description = row[4].strip()
            interpro_id = row[5].strip()
            interpro_description = row[6].strip()

            if source_key == 'JASPAR':
                pass
            elif source_key == 'HMMSmart':
                source_key = 'SMART'
            elif source_key == 'HMMPfam':
                source_key = 'Pfam'
            elif source_key == 'Gene3D':
                pass
            elif source_key == 'superfamily':
                source_key = 'SUPERFAMILY'
            elif source_key == 'Seg':
                source_key = '-'
            elif source_key == 'Coil':
                source_key = '-'
            elif source_key == 'HMMPanther':
                source_key = 'PANTHER'
            elif source_key == 'HMMTigr':
                source_key = 'TIGRFAMs'
            elif source_key == 'FPrintScan':
                source_key = 'PRINTS'
            elif source_key == 'BlastProDom':
                source_key = 'ProDom'
            elif source_key == 'HMMPIR':
                source_key = "PIR superfamily"
            elif source_key == 'ProfileScan':
                source_key = 'PROSITE'
            elif source_key == 'PatternScan':
                source_key = 'PROSITE'
            else:
                print 'No source translation ' + source_key + ' ' + str(display_name)
                yield None

            source_key = create_format_name(source_key)
            source = None if source_key not in key_to_source else key_to_source[source_key]

            description = None if description == 'no description' else description
            interpro_description = None if interpro_description == 'NULL' else interpro_description
            interpro_id = None if interpro_id == 'NULL' else interpro_id

            if source_key == 'PANTHER':
                if display_name in panther_id_to_description:
                    yield {'display_name': display_name,
                       'source': source,
                       'description': panther_id_to_description[display_name],
                       'bioitem_type': source_key,
                       'interpro_id': interpro_id,
                       'interpro_description': interpro_description}
                else:
                    not_a_panther_id.add(display_name)

            else:
                yield {'display_name': display_name,
                       'source': source,
                       'description': description if description is not None else interpro_description,
                       'bioitem_type': source_key,
                       'interpro_id': interpro_id,
                       'interpro_description': interpro_description}

        print 'Not a panther ID: ' + str(not_a_panther_id)

        for row in make_file_starter('src/sgd/convert/data/TF_family_class_accession04302013.txt')():
            description = 'Class: ' + row[4] + ', Family: ' + row[3]
            yield {'display_name': row[0],
                   'source': key_to_source['JASPAR'],
                   'description': description,
                   'bioitem_type': 'JASPAR'}

        yield {'display_name': 'predicted signal peptide',
               'source': key_to_source['SignalP'],
               'description': 'predicted signal peptide',
               'bioitem_type': 'SignalP'}
        yield {'display_name': 'predicted transmembrane domain',
               'source': key_to_source['TMHMM'],
               'description': 'predicted transmembrane domain',
               'bioitem_type': 'TMHMM'}

        not_a_panther_id = set()

        for bud_obj in make_db_starter(bud_session.query(Dbxref).filter(or_(Dbxref.dbxref_type == 'PANTHER', Dbxref.dbxref_type == 'Prosite')), 1000)():
            dbxref_type = bud_obj.dbxref_type
            source_key = create_format_name(bud_obj.source)
            source = None if source_key not in key_to_source else key_to_source[source_key]
            if source is None:
                print source_key
                yield None
            bioitem_type = None
            if dbxref_type == 'Prosite ID':
                bioitem_type = 'Prosite'
            elif dbxref_type == 'PANTHER':
                bioitem_type = 'PANTHER'

            if bioitem_type == 'PANTHER':
                if display_name in panther_id_to_description:
                    yield {'display_name': bud_obj.dbxref_id,
                       'source': source,
                       'description': panther_id_to_description[bud_obj.dbxref_id],
                       'bioitem_type': bioitem_type}
                else:
                    not_a_panther_id.add(bud_obj.dbxref_id)
            else:
                yield {'display_name': bud_obj.dbxref_id,
                       'source': source,
                       'description': bud_obj.dbxref_name,
                       'bioitem_type': bioitem_type}

        print 'Not a panther ID: ' + str(not_a_panther_id)

        bud_session.close()
        nex_session.close()
    return domain_starter

# --------------------- Convert Chemical ---------------------
def make_chemical_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.cv import CVTerm
    from src.sgd.model.bud.phenotype import ExperimentProperty

    def chemical_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no == 3), 1000)():
            yield {'display_name': bud_obj.name,
                   'source': key_to_source['SGD'],
                   'chebi_id': bud_obj.dbxref_id,
                   'description': bud_obj.definition,
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        for bud_obj in make_db_starter(bud_session.query(ExperimentProperty).filter(or_(ExperimentProperty.type=='Chemical_pending', ExperimentProperty.type == 'chebi_ontology')), 1000)():
            yield {'display_name': bud_obj.value,
                   'source': key_to_source['SGD'],
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        bud_session.close()
        nex_session.close()
    return chemical_starter

# --------------------- Convert Contig ---------------------
def make_contig_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.convert.from_bud import sequence_files

    def contig_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

        for sequence_filename, coding_sequence_filename, strain in sequence_files:
            filenames = []
            if isinstance(sequence_filename, list):
                filenames = sequence_filename
            elif sequence_filename is not None:
                filenames.append(sequence_filename)
            for filename in filenames:
                for sequence_id, residues in make_fasta_file_starter(filename)():
                    yield {'display_name': sequence_id,
                           'source': key_to_source['SGD'],
                           'strain': key_to_strain[strain.replace('.', '')],
                           'residues': residues}
        nex_session.close()
    return contig_starter

# --------------------- Convert Relation ---------------------
def make_bioitem_relation_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioitem import Chemical
    from src.sgd.model.bud.cv import CVTermRel

    def bioitem_relation_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_chemical = dict([(x.unique_key(), x) for x in nex_session.query(Chemical).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_db_starter(bud_session.query(CVTermRel).options(joinedload('child'), joinedload('parent')), 1000)():
            parent_key = (create_format_name(bud_obj.parent.name)[:95], 'CHEMICAL')
            child_key = (create_format_name(bud_obj.child.name)[:95], 'CHEMICAL')

            if parent_key in key_to_chemical and child_key in key_to_chemical:
                yield {'source': key_to_source['SGD'],
                       'relation_type': bud_obj.relationship_type,
                       'parent_id': key_to_chemical[parent_key].id,
                       'child_id': key_to_chemical[child_key].id,
                       'date_created': bud_obj.date_created,
                       'created_by': bud_obj.created_by}

        bud_session.close()
        nex_session.close()
    return bioitem_relation_starter

# --------------------- Convert Bioitem URL ---------------------
def make_bioitem_url_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioitem import Domain, Chemical

    def bioitem_url_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for domain in make_db_starter(nex_session.query(Domain), 1000)():
            bioitem_type = domain.source.unique_key()
            display_name = domain.display_name
            if bioitem_type == 'JASPAR':
                link = 'http://jaspar.binf.ku.dk/cgi-bin/jaspar_db.pl?rm=present&collection=CORE&ID=' + display_name
            elif bioitem_type == 'SMART':
                link = "http://smart.embl-heidelberg.de/smart/do_annotation.pl?DOMAIN=" + display_name
            elif bioitem_type == 'Pfam':
                link = "http://pfam.sanger.ac.uk/family?type=Family&entry=" + display_name
            elif bioitem_type == 'Gene3D':
                link = "http://www.cathdb.info/version/latest/superfamily/" + display_name[6:]
            elif bioitem_type == 'SUPERFAMILY':
                link = "http://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid=" + display_name
            elif bioitem_type == 'SignalP':
                link = None
            elif bioitem_type == 'PANTHER':
                link = "http://www.pantherdb.org/panther/family.do?clsAccession=" + display_name
            elif bioitem_type == 'TIGRFAMs':
                link = "http://cmr.tigr.org/tigr-scripts/CMR/HmmReport.cgi?hmm_acc=" + display_name
            elif bioitem_type == 'PRINTS':
                link = "http:////www.bioinf.man.ac.uk/cgi-bin/dbbrowser/sprint/searchprintss.cgi?display_opts=Prints&amp;category=None&amp;queryform=false&amp;prints_accn=" + display_name
            elif bioitem_type == 'ProDom':
                link = "http://prodom.prabi.fr/prodom/current/cgi-bin/request.pl?question=DBEN&amp;query=" + display_name
            elif bioitem_type == 'PIR_superfamily':
                link = "http://pir.georgetown.edu/cgi-bin/ipcSF?" + display_name
            elif bioitem_type == 'PROSITE':
                link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
            elif bioitem_type == 'PROSITE':
                link = "http://prodom.prabi.fr/prodom/cgi-bin/prosite-search-ac?" + display_name
            else:
                print 'No link for source = ' + str(bioitem_type) + ' ' + str(display_name)
                link = None

            if link is not None:
                yield {'display_name': display_name,
                       'link': link,
                       'source': key_to_source['SGD'],
                       'category': 'External',
                       'bioitem_id': domain.id}
            if domain.interpro_id is not None:
                yield {'display_name': domain.interpro_id,
                       'link': 'http://www.ebi.ac.uk/interpro/entry/' + domain.interpro_id,
                       'source': key_to_source['InterPro'],
                       'category': 'Interpro',
                       'bioitem_id': domain.id}

        for chemical in make_db_starter(nex_session.query(Chemical), 1000)():
            if chemical.chebi_id is not None:
                yield {'display_name': chemical.chebi_id,
                       'link': 'http://www.ebi.ac.uk/chebi/searchId.do?chebiId=' + chemical.chebi_id,
                       'source': key_to_source['SGD'],
                       'category': 'External',
                       'bioitem_id': chemical.id}

        nex_session.close()
    return bioitem_url_starter