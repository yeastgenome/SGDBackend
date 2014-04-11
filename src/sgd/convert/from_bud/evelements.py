from sqlalchemy.orm import joinedload

from src.sgd.convert.transformers import make_db_starter, make_file_starter, \
    make_obo_file_starter


__author__ = 'kpaskov'

#Recorded times: 
#Maitenance (cherry-vm08): 0:01, 
#First Load (sgd-ng1): :09, :10
#1.23.14 Maitenance (sgd-dev): :06

# --------------------- Convert Experiment ---------------------
def make_experiment_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.cv import CVTerm
    def experiment_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_obo_file_starter('src/sgd/convert/data/eco.obo')():
            yield {'display_name': bud_obj['name'],
                   'source': key_to_source['ECO'],
                   'description': None if 'def' not in bud_obj else bud_obj['def'],
                   'eco_id': bud_obj['id']}

        for bud_obj in make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no==7), 1000)():
            yield {'display_name': bud_obj.name,
                   'source': key_to_source['SGD'],
                   'description': bud_obj.definition,
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        for row in make_file_starter('src/sgd/convert/data/yeastmine_regulation.tsv')():
            source_key = row[12].strip()
            yield {'display_name': row[4],
                   'source': None if source_key not in key_to_source else key_to_source[source_key],
                   'eco_id': row[5]}

        for row in make_file_starter('src/sgd/convert/data/yetfasco_data.txt', delimeter=';')():
            yield {'display_name': row[9][1:-1],
                   'source': key_to_source['YeTFaSCo']}

        for row in make_file_starter('src/sgd/convert/data/phosphosites.txt', delimeter=';')():
            if len(row) > 3:
                for display_name in row[3].split('|'):
                    yield {'display_name': display_name,
                           'source': key_to_source['PhosphoGRID']}

        yield {'display_name': 'protein abundance',
               'source': key_to_source['SGD']}

        bud_session.close()
        nex_session.close()
    return experiment_starter

# --------------------- Convert Experiment Alias ---------------------
def make_experiment_alias_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Experiment
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.bud.cv import CVTerm
    def experiment_alias_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_cv_term in make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no==7).options(joinedload('cv_dbxrefs'), joinedload('cv_dbxrefs.dbxref')), 1000)():
            experiment_key = create_format_name(old_cv_term.name)
            if experiment_key in key_to_experiment:
                for dbxref in old_cv_term.dbxrefs:
                    yield {'display_name': dbxref.dbxref_id,
                           'source': key_to_source['SGD'],
                           'category': 'APOID',
                           'experiment_id': key_to_experiment[experiment_key].id,
                           'date_created': dbxref.date_created,
                           'created_by': dbxref.created_by}
            else:
                print 'Experiment does not exist: ' + str(experiment_key)
                yield None

        bud_session.close()
        nex_session.close()
    return experiment_alias_starter

# --------------------- Convert Experiment Relation ---------------------
def make_experiment_relation_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Experiment
    from src.sgd.model.nex import create_format_name
    from src.sgd.model.bud.cv import CVTerm
    def experiment_relation_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_cv_term in make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no==7).options(joinedload('parent_rels'), joinedload('parent_rels.parent')), 1000)():
            child_key = create_format_name(old_cv_term.name)
            for parent_rel in old_cv_term.parent_rels:
                parent_key = create_format_name(parent_rel.parent.name)
                if parent_key in key_to_experiment and child_key in key_to_experiment:
                    yield {'source': key_to_source['SGD'],
                           'parent_id': key_to_experiment[parent_key].id,
                           'child_id': key_to_experiment[child_key].id,
                           'date_created': parent_rel.date_created,
                           'created_by': parent_rel.created_by}
                else:
                    print 'Experiment does not exist: ' + str(parent_key) + ' ' + str(child_key)

        bud_session.close()
        nex_session.close()
    return experiment_relation_starter

# --------------------- Convert Strain ---------------------
def make_strain_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.cv import CVTerm
    def strain_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_db_starter(bud_session.query(CVTerm).filter(CVTerm.cv_no==10), 1000)():
            yield {'display_name': bud_obj.name,
                   'source': key_to_source['SGD'],
                   'description': bud_obj.definition,
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        other_strains = [('AWRI1631', 'Haploid derivative of South African commercial wine strain N96.'),
                                   ('AWRI796', 'South African red wine strain.'),
                                   ('BY4741', 'S288C-derivative laboratory strain.'),
                                   ('BY4742', 'S288C-derivative laboratory strain.'),
                                   ('CBS7960', 'Brazilian bioethanol factory isolate.'),
                                   ('CLIB215', 'New Zealand bakery isolate.'),
                                   ('CLIB324', 'Vietnamese bakery isolate.'),
                                   ('CLIB382', 'Irish beer isolate.'),
                                   ('EC1118', 'Commercial wine strain.'),
                                   ('EC9-8', 'Haploid derivative of Israeli canyon isolate.'),
                                   ('FostersB', 'Commercial ale strain.'),
                                   ('FostersO', 'Commercial ale strain.'),
                                   ('JAY291', 'Haploid derivative of Brazilian industrial bioethanol strain PE-2.'),
                                   ('Kyokai7', 'Japanese sake yeast.'),
                                   ('LalvinQA23', 'Portuguese Vinho Verde white wine strain.'),
                                   ('M22', 'Italian vineyard isolate.'),
                                   ('PW5', 'Nigerian Raphia palm wine isolate.'),
                                   ('T7', 'Missouri oak tree exudate isolate.'),
                                   ('T73', 'Spanish red wine strain.'),
                                   ('UC5', 'Japanese sake yeast.'),
                                   ('VIN13', 'South African white wine strain.'),
                                   ('VL3', 'French white wine strain.'),
                                   ('Y10', 'Philippine coconut isolate.'),
                                   ('YJM269', 'Austrian Blauer Portugieser wine grape isolate.'),
                                   ('YJM789', 'Haploid derivative of opportunistic human pathogen.'),
                                   ('YPS163', 'Pennsylvania woodland isolate.'),
                                   ('ZTW1', 'Chinese corn mash bioethanol isolate.')]

        for strain, description in other_strains:
            yield {'display_name': strain,
                   'source': key_to_source['SGD'],
                   'description': description}

        bud_session.close()
        nex_session.close()
    return strain_starter

# --------------------- Convert Source ---------------------
def make_source_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.bud.cv import Code
    def source_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        for bud_obj in make_db_starter(bud_session.query(Code), 1000)():
            if (bud_obj.tab_name, bud_obj.col_name) in ok_codes:
                yield {'display_name': bud_obj.code_value,
                       'description': bud_obj.description,
                       'date_created': bud_obj.date_created,
                       'created_by': bud_obj.created_by}

        other_sources = ['SGD', 'GO', 'PROSITE', 'Gene3D', 'SUPERFAMILY', 'TIGRFAMs', 'Pfam', 'PRINTS',
                                        'PIR superfamily', 'JASPAR', 'SMART', 'PANTHER', 'ProDom', 'DOI',
                                        'PubMedCentral', 'PubMed', '-', 'ECO', 'TMHMM', 'SignalP', 'PhosphoGRID',
                                        'GenBank/EMBL/DDBJ']

        for source in other_sources:
            yield {'display_name': source}

        bud_session.close()
        nex_session.close()
    return source_starter

ok_codes = {('ALIAS', 'ALIAS_TYPE'), ('DBXREF', 'SOURCE'), ('EXPERIMENT', 'SOURCE'), ('FEATURE', 'SOURCE'),
                ('GO_ANNOTATION', 'SOURCE'), ('HOMOLOG', 'SOURCE'), ('INTERACTION', 'SOURCE'), ('PHENOTYPE', 'SOURCE'),
                ('REFTYPE', 'SOURCE'), ('REFERENCE', 'SOURCE'), ('URL', 'SOURCE')}
