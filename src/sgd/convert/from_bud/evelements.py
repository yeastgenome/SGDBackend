from sqlalchemy.orm import joinedload

from src.sgd.convert.transformers import make_file_starter, \
    make_obo_file_starter
from src.sgd.convert import create_format_name
from src.sgd.model.nex.misc import Source


__author__ = 'kpaskov'

#Recorded times: 
#Maitenance (cherry-vm08): 0:01, 
#First Load (sgd-ng1): :09, :10
#1.23.14 Maitenance (sgd-dev): :06

# --------------------- Convert Experiment ---------------------
def make_experiment_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.bud.cv import CVTerm

    def experiment_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_obo_file_starter('src/sgd/convert/data/eco.obo')():
            description = None if 'def' not in bud_obj else bud_obj['def']
            if description is not None and description.find('[') >= 0:
                description = description[:description.find('[')-1]
            if description is not None and description.find('"') >= 0:
                description = description[1:-1]
            yield {'display_name': bud_obj['name'],
                   'source': key_to_source['ECO'],
                   'description': description,
                   'eco_id': bud_obj['id']}

        for bud_obj in bud_session.query(CVTerm).filter(CVTerm.cv_no==7).all():
            format_name = create_format_name(bud_obj.name)
            yield {'display_name': bud_obj.name,
                   'source': key_to_source['SGD'],
                   'description': bud_obj.definition,
                   'category': 'large-scale survey' if format_name in large_scale_survey else 'classical genetics' if format_name in classical_genetics else None,
                   'date_created': bud_obj.date_created,
                   'created_by': bud_obj.created_by}

        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Venters_Macisaac_Hu05-12-2014_regulator_lines')():
            source_key = row[11].strip()
            if source_key in key_to_source:
                yield {'display_name': row[4] if row[4] != '' else row[5],
                       'source': None if source_key not in key_to_source else key_to_source[source_key],
                       'eco_id': row[5]}
            else:
                print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/SGD_data_05_14_2014')():
            source_key = row[11].strip()
            if source_key in key_to_source:
                yield {'display_name': row[4] if row[4] != '' else row[5],
                       'source': None if source_key not in key_to_source else key_to_source[source_key],
                       'eco_id': row[5]}
            else:
                print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Madhani_fixed')():
            if len(row) >= 10:
                if source_key in key_to_source:
                    source_key = row[11].strip()
                    yield {'display_name': row[5] if row[5] != '' else row[4],
                           'source': None if source_key not in key_to_source else key_to_source[source_key],
                           'eco_id': row[4]}
                else:
                    print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Pimentel_PMID22616008.txt')():
            if len(row) >= 10:
                if source_key in key_to_source:
                    source_key = row[11].strip()
                    yield {'display_name': row[4] if row[4] != '' else row[5],
                           'source': None if source_key not in key_to_source else key_to_source[source_key],
                           'eco_id': row[5]}
                else:
                    print 'Source not found: ' + str(source_key)

        for row in make_file_starter('src/sgd/convert/data/yetfasco_data.txt', delimeter=';')():
            expert_confidence = row[8][1:-1]
            if expert_confidence == 'High':
                yield {'display_name': row[9][1:-1],
                    'source': key_to_source['YeTFaSCo']}

        yield {'display_name': 'protein abundance', 'source': key_to_source['SGD']}
        yield {'display_name': 'EXP', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/exp-inferred-experiment', 'description': 'Inferred from Experiment'}
        yield {'display_name': 'IDA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ida-inferred-direct-assay', 'description': 'Inferred from Direct Assay'}
        yield {'display_name': 'IPI', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ipi-inferred-physical-interaction', 'description': 'Inferred from Physical Interaction'}
        yield {'display_name': 'IMP', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/imp-inferred-mutant-phenotype', 'description': 'Inferred from Mutant Phenotype'}
        yield {'display_name': 'IGI', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/igi-inferred-genetic-interaction', 'description': 'Inferred from Genetic Interaction'}
        yield {'display_name': 'IEP', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/iep-inferred-expression-pattern', 'description': 'Inferred from Expression Pattern'}
        yield {'display_name': 'ISS', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/iss-inferred-sequence-or-structural-similarity', 'description': 'Inferred from Sequence or Structural Similarity'}
        yield {'display_name': 'ISA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/isa-inferred-sequence-alignment', 'description': 'Inferred from Sequence Alignment'}
        yield {'display_name': 'ISO', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/iso-inferred-sequence-orthology', 'description': 'Inferred from Sequence Orthology'}
        yield {'display_name': 'ISM', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ism-inferred-sequence-model', 'description': 'Inferred from Sequence Model'}
        yield {'display_name': 'IGC', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/igc-inferred-genomic-context', 'description': 'Inferred from Genomic Context'}
        yield {'display_name': 'IBA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/iba-inferred-biological-aspect-ancestor', 'description': 'Inferred from Biological aspect of Ancestor'}
        yield {'display_name': 'IBD', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ibd-inferred-biological-aspect-descendent', 'description': 'Inferred from Biological aspect of Descendent'}
        yield {'display_name': 'IKR', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ikr-inferred-key-residues', 'description': 'Inferred from Key Residues'}
        yield {'display_name': 'IRD', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ird-inferred-rapid-divergence', 'description': 'Inferred from Rapid Divergence'}
        yield {'display_name': 'RCA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/rca-inferred-reviewed-computational-analysis', 'description': 'inferred from Reviewed Computational Analysis'}
        yield {'display_name': 'TAS', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/tas-traceable-author-statement', 'description': 'Traceable Author Statement'}
        yield {'display_name': 'NAS', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/nas-non-traceable-author-statement', 'description': 'Non-traceable Author Statement'}
        yield {'display_name': 'IC', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/ic-inferred-curator', 'description': 'Inferred by Curator'}
        yield {'display_name': 'ND', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/nd-no-biological-data-available', 'description': 'No Biological Data Available'}
        yield {'display_name': 'IEA', 'source': key_to_source['GO'], 'link': 'http://www.geneontology.org/page/automatically-assigned-evidence-codes', 'description': 'Inferred from Electronic Annotation'}

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

        for old_cv_term in bud_session.query(CVTerm).filter(CVTerm.cv_no==7).options(joinedload('cv_dbxrefs'), joinedload('cv_dbxrefs.dbxref')).all():
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

        for old_cv_term in bud_session.query(CVTerm).filter(CVTerm.cv_no==7).options(joinedload('parent_rels'), joinedload('parent_rels.parent')).all():
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


# --------------------- Convert Alias Reference ---------------------
def make_alias_reference_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Bioentityalias
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reflink as OldReflink
    from src.sgd.model.bud.feature import AliasFeature as OldAliasFeature
    from src.sgd.model.bud.general import DbxrefFeat as OldDbxrefFeat
    def alias_reference_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_alias = dict([(x.unique_key(), x) for x in nex_session.query(Bioentityalias).all()])

        feat_alias_id_to_reflinks = dict()
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_ALIAS').all():
            if reflink.primary_key in feat_alias_id_to_reflinks:
                feat_alias_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                feat_alias_id_to_reflinks[reflink.primary_key] = [reflink]

        dbxref_feat_id_to_reflinks = dict()
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='DBXREF_FEAT').all():
            if reflink.primary_key in dbxref_feat_id_to_reflinks:
                dbxref_feat_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                dbxref_feat_id_to_reflinks[reflink.primary_key] = [reflink]

        for old_alias in bud_session.query(OldAliasFeature).options(joinedload('alias')).all():
            bioentity_id = old_alias.feature_id
            alias_key = 'BIOENTITY', old_alias.alias_name, str(bioentity_id), 'Alias' if old_alias.alias_type == 'Uniform' or old_alias.alias_type == 'Non-uniform' else old_alias.alias_type

            if old_alias.id in feat_alias_id_to_reflinks:
                for reflink in feat_alias_id_to_reflinks[old_alias.id]:
                    reference_id = reflink.reference_id
                    if alias_key in key_to_alias and reference_id in id_to_reference:
                        yield {
                            'alias_id': key_to_alias[alias_key].id,
                            'reference_id': id_to_reference[reference_id].id,
                        }
                    else:
                        print 'Reference or alias not found: ' + str(reference_id) + ' ' + str(alias_key)

        for old_dbxref_feat in bud_session.query(OldDbxrefFeat).options(joinedload(OldDbxrefFeat.dbxref), joinedload('dbxref.dbxref_urls')).all():
            if old_dbxref_feat.dbxref.dbxref_type != 'DBID Primary':
                bioentity_id = old_dbxref_feat.feature_id
                alias_key = 'BIOENTITY', old_dbxref_feat.dbxref.dbxref_id, str(bioentity_id), old_dbxref_feat.dbxref.dbxref_type

                if old_dbxref_feat.id in dbxref_feat_id_to_reflinks:
                    for reflink in dbxref_feat_id_to_reflinks[old_dbxref_feat.id]:
                        reference_id = reflink.reference_id
                        if alias_key in key_to_alias and reference_id in id_to_reference:
                            yield {
                                'alias_id': key_to_alias[alias_key].id,
                                'reference_id': id_to_reference[reference_id].id,
                            }
                        else:
                            print 'Reference or alias not found: ' + str(reference_id) + ' ' + str(alias_key)

        bud_session.close()
        nex_session.close()
    return alias_reference_starter

# --------------------- Convert Relation Reference ---------------------
def make_relation_reference_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Bioentityrelation
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reflink as OldReflink
    from src.sgd.model.bud.feature import FeatRel
    def alias_reference_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_relation = dict([(x.unique_key(), x) for x in nex_session.query(Bioentityrelation).all()])

        relation_id_to_reflinks = dict()
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_RELATIONSHIP').all():
            if reflink.primary_key in relation_id_to_reflinks:
                relation_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                relation_id_to_reflinks[reflink.primary_key] = [reflink]

        for old_relation in bud_session.query(FeatRel).filter_by(relationship_type='pair').all():
             relation1_key = (str(old_relation.parent_id) + ' - ' + str(old_relation.child_id), 'BIOENTITY', 'paralog')
             relation2_key = (str(old_relation.child_id) + ' - ' + str(old_relation.parent_id), 'BIOENTITY', 'paralog')

             if old_relation.id in relation_id_to_reflinks:
                for reflink in relation_id_to_reflinks[old_relation.id]:
                    reference_id = reflink.reference_id
                    if relation1_key in key_to_relation and reference_id in id_to_reference:
                        yield {
                            'relation_id': key_to_relation[relation1_key].id,
                            'reference_id': id_to_reference[reference_id].id,
                        }
                    else:
                        print 'Reference or relation not found: ' + str(reference_id) + ' ' + str(relation1_key)

                    if relation2_key in key_to_relation and reference_id in id_to_reference:
                        yield {
                            'relation_id': key_to_relation[relation2_key].id,
                            'reference_id': id_to_reference[reference_id].id,
                        }
                    else:
                        print 'Reference or relation not found: ' + str(reference_id) + ' ' + str(relation2_key)

        bud_session.close()
        nex_session.close()
    return alias_reference_starter

bad_quality_references = {37408}
def make_quality_reference_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Strain, Quality
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reflink as OldReflink
    from src.sgd.model.bud.feature import Annotation as OldAnnotation, FeatureProperty as OldFeatureProperty
    def quality_reference_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_quality = dict([(x.unique_key(), x) for x in nex_session.query(Quality).all()])

        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_ANNOTATION').all():
            if reflink.col_name != 'DNA binding motif':
                if reflink.primary_key in id_to_bioentity:
                    reference_id = reflink.reference_id
                    if reference_id not in bad_quality_references:
                        quality_key = None
                        if reflink.col_name == 'QUALIFIER':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Qualifier')
                        elif reflink.col_name == 'NAME_DESCRIPTION':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Name Description')
                        elif reflink.col_name == 'DESCRIPTION':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Description')
                        elif reflink.col_name == 'GENETIC_POSITION':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Genetic Position')
                        elif reflink.col_name == 'HEADLINE':
                            quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Headline')

                        if quality_key is None:
                            print 'Column not found: ' + reflink.col_name
                        elif quality_key in key_to_quality and reference_id in id_to_reference:
                            yield {
                                    'quality_id': key_to_quality[quality_key].id,
                                    'reference_id': id_to_reference[reference_id].id,
                                 }
                        else:
                            print 'Quality or reference not found: ' + str(quality_key) + ' ' + str(reference_id)
                else:
                    #print 'Bioentity not found: ' + str(reflink.primary_key)
                    yield None

        id_to_feat_property = dict([(x.id, x) for x in bud_session.query(OldFeatureProperty).all()])
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_PROPERTY').all():
            if reflink.primary_key in id_to_feat_property:
                feat_property = id_to_feat_property[reflink.primary_key]
                reference_id = reflink.reference_id
                if reference_id not in bad_quality_references:
                    quality_key = (str(feat_property.feature_id), 'BIOENTITY', feat_property.property_type)

                    if quality_key in key_to_quality and reference_id in id_to_reference:
                        yield {
                                'quality_id': key_to_quality[quality_key].id,
                                'reference_id': id_to_reference[reference_id].id,
                             }
                    else:
                        print 'Quality or reference not found: ' + str(quality_key) + ' ' + str(reference_id)
            else:
                print 'Feature property not found: ' + str(reflink.primary_key)

        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEATURE').all():
            if reflink.primary_key in id_to_bioentity:
                quality_key = None
                reference_id = reflink.reference_id
                if reference_id not in bad_quality_references:
                    if reflink.col_name == 'GENE_NAME':
                        quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Gene Name')
                    elif reflink.col_name == 'FEATURE_TYPE':
                        quality_key = (str(reflink.primary_key), 'BIOENTITY', 'Feature Type')
                    elif reflink.col_name == 'FEATURE_NO':
                        quality_key = (str(reflink.primary_key), 'BIOENTITY', 'ID')

                    if quality_key is None:
                        print 'Column not found : ' + reflink.col_name
                    elif quality_key in key_to_quality and reference_id in id_to_reference:
                        yield {
                                'quality_id': key_to_quality[quality_key].id,
                                'reference_id': id_to_reference[reference_id].id,
                             }
                    else:
                        print 'Quality or reference not found: ' + str(quality_key) + ' ' + str(reference_id)
            else:
                #print 'Bioentity not found: ' + str(reflink.primary_key)
                yield None

        bud_session.close()
        nex_session.close()
    return quality_reference_starter