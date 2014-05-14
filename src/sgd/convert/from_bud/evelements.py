from sqlalchemy.orm import joinedload

from src.sgd.convert.transformers import make_db_starter, make_file_starter, \
    make_obo_file_starter
from src.sgd.convert import create_format_name


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
            format_name = create_format_name(bud_obj.name)
            yield {'display_name': bud_obj.name,
                   'source': key_to_source['SGD'],
                   'description': bud_obj.definition,
                   'category': 'large-scale survey' if format_name in large_scale_survey else 'classical genetics' if format_name in classical_genetics else None,
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        for row in make_file_starter('src/sgd/convert/data/regulation_data_05_14/Venters_Macisaac_Hu05-12-2014_regulator_lines')():
            source_key = row[11].strip()
            if source_key in key_to_source:
                yield {'display_name': row[4] if row[4] != '' else row[5],
                       'source': None if source_key not in key_to_source else key_to_source[source_key],
                       'eco_id': row[5]}
            else:
                print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/regulation_data_05_14/SGD_data_05_13_2014')():
            source_key = row[11].strip()
            if source_key in key_to_source:
                yield {'display_name': row[4] if row[4] != '' else row[5],
                       'source': None if source_key not in key_to_source else key_to_source[source_key],
                       'eco_id': row[5]}
            else:
                print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/regulation_data_05_14/Madhani_manual_data.txt')():
            if len(row) >= 10:
                if source_key in key_to_source:
                    source_key = row[11].strip()
                    yield {'display_name': row[4] if row[4] != '' else row[5],
                           'source': None if source_key not in key_to_source else key_to_source[source_key],
                           'eco_id': row[5]}
                else:
                    print 'Source not found: ' + str(source_key)

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

large_scale_survey = {'large-scale_survey', 'competitive_growth', 'heterozygous_diploid,_large-scale_survey', 'homozygous_diploid,_large-scale_survey', 'systematic_mutation_set', 'heterozygous_diploid,_competitive_growth',
                      'homozygous_diploid,_competitive_growth', 'heterozygous_diploid,_systematic_mutation_set', 'homozygous_diploid,_systematic_mutation_set'}
classical_genetics = {'classical_genetics', 'heterozygous_diploid', 'homozygous_diploid'}

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
alternative_reference_strains = {'CEN.PK', 'D273-10B', 'FL100', 'JK9-3d', 'RM11-1a', 'SEY6210', 'SK1', 'Sigma1278b', 'W303', 'X2180-1A', 'Y55'}

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
                   'status': 'Reference' if bud_obj.name == 'S288C' else ('Alternative Reference' if bud_obj.name in alternative_reference_strains else 'Other'),
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        other_strains = [('10560-6B', 'Sigma1278b-derivative laboratory strain.'),
                                   ('AWRI1631', 'Haploid derivative of South African commercial wine strain N96.'),
                                   ('AWRI796', 'South African red wine strain.'),
                                   ('BC187', 'Derivative of California wine barrel isolate.'),
                                   ('BY4741', 'S288C-derivative laboratory strain.'),
                                   ('BY4742', 'S288C-derivative laboratory strain.'),
                                   ('CBS7960', 'Brazilian bioethanol factory isolate.'),
                                   ('CLIB215', 'New Zealand bakery isolate.'),
                                   ('CLIB324', 'Vietnamese bakery isolate.'),
                                   ('CLIB382', 'Irish beer isolate.'),
                                   ('D273', 'Laboratory strain.'),
                                   ('DBVPG6044', 'West African isolate.'),
                                   ('EC1118', 'Commercial wine strain.'),
                                   ('EC9-8', 'Haploid derivative of Israeli canyon isolate.'),
                                   ('FL100', 'Laboratory strain.'),
                                   ('FostersB', 'Commercial ale strain.'),
                                   ('FostersO', 'Commercial ale strain.'),
                                   ('FY1679', 'S288C-derivative laboratory strain.'),
                                   ('JAY291', 'Haploid derivative of Brazilian industrial bioethanol strain PE-2.'),
                                   ('JK9', 'Laboratory strain.'),
                                   ('K11', 'Sake strain.'),
                                   ('Kyokai7', 'Japanese sake yeast.'),
                                   ('L1528', 'Chilean wine strain.'),
                                   ('LalvinQA23', 'Portuguese Vinho Verde white wine strain.'),
                                   ('M22', 'Italian vineyard isolate.'),
                                   ('PW5', 'Nigerian Raphia palm wine isolate.'),
                                   ('RedStar', 'Commercial baking strain.'),
                                   ('RM11-1A', 'Haploid derivative of California vineyard isolate.'),
                                   ('SEY', 'Laboratory strain.'),
                                   ('SK1', 'Laboratory strain.'),
                                   ('T7', 'Missouri oak tree exudate isolate.'),
                                   ('T73', 'Spanish red wine strain.'),
                                   ('UC5', 'Japanese sake yeast.'),
                                   ('UWOPSS', 'Environmental isolate.'),
                                   ('VIN13', 'South African white wine strain.'),
                                   ('VL3', 'French white wine strain.'),
                                   ('W303', 'Laboratory strain.'),
                                   ('X2180', 'S288C-derivative laboratory strain.'),
                                   ('Y10', 'Philippine coconut isolate.'),
                                   ('Y55', 'Laboratory strain.'),
                                   ('YJM269', 'Austrian Blauer Portugieser wine grape isolate.'),
                                   ('YJM339', 'Clinical isolate.'),
                                   ('YJM789', 'Haploid derivative of opportunistic human pathogen.'),
                                   ('YPH499', 'S288C-congenic laboratory strain.'),
                                   ('YPS128', 'Pennsylvania woodland isolate.'),
                                   ('YPS163', 'Pennsylvania woodland isolate.'),
                                   ('YS9', 'Singapore baking strain.'),
                                   ('ZTW1', 'Chinese corn mash bioethanol isolate.')]

        for strain, description in other_strains:
            yield {'display_name': strain,
                   'source': key_to_source['SGD'],
                   'description': description,
                   'status': 'Reference' if bud_obj.name == 'S288C' else ('Alternative Reference' if strain in alternative_reference_strains else 'Other')}

        bud_session.close()
        nex_session.close()
    return strain_starter

# --------------------- Convert Strain Url ---------------------
wiki_strains = set(['S288C', 'BY4743', 'FY4', 'DBY12020', 'DBY12021', 'FY1679', 'AB972', 'A364A', 'XJ24-24a', 'DC5', 'X2180-1A',
                'YNN216', 'YPH499', 'YPH500', 'YPH501', 'Sigma1278b', 'SK1', 'CEN.PK', 'W303', 'W303-1A',
                'W303-1B', 'W303-K6001', 'DY1457', 'D273-10B', 'FL100', 'SEY6210/SEY6211', 'SEY6210', 'SEY6211',
                'JK9-3d', 'RM11-1a', 'Y55'])
sequence_download_strains = set(['AWRI1631', 'AWRI796', 'BY4741', 'BY4742', 'CBS7960', 'CEN.PK', 'CLIB215', 'CLIB324',
                                'CLIB382', 'EC1118', 'EC9-8', 'FL100', 'FostersB', 'FostersO', 'JAY291', 'Kyokai7',
                                'LalvinQA23', 'M22', 'PW5', 'RM11-1a', 'Sigma1278b', 'T7', 'T73', 'UC5', 'VIN13', 'VL3',
                                'W303', 'Y10', 'YJM269', 'YJM789', 'YPS163', 'ZTW1'])
def make_strain_url_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source, Strain
    def strain_url_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

        for strain in key_to_strain.values():
            if strain.display_name in wiki_strains:
                yield {'display_name': 'Wiki',
                               'link': 'http://wiki.yeastgenome.org/index.php/Commonly_used_strains#' + strain.display_name,
                               'source': key_to_source['SGD'],
                               'category': 'wiki',
                               'strain': strain}

            if strain.display_name in sequence_download_strains:
                yield {'display_name': 'Download Sequence',
                               'link': 'http://downloads.yeastgenome.org/sequence/strains/' + strain.display_name,
                               'source': key_to_source['SGD'],
                               'category': 'download',
                               'strain': strain}

        yield {'display_name': 'Download Sequence',
                               'link': 'http://www.yeastgenome.org/download-data/sequence',
                               'source': key_to_source['SGD'],
                               'category': 'download',
                               'strain': key_to_strain['S288C']}

        nex_session.close()
    return strain_url_starter

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
