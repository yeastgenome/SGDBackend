from decimal import Decimal
from sqlalchemy.orm import joinedload
from datetime import datetime

from src.sgd.convert.from_bud import contains_digits, get_dna_sequence_library, get_sequence, get_sequence_library_fsa, reverse_complement
from src.sgd.convert.transformers import make_db_starter, make_file_starter
from src.sgd.model.nex import create_format_name
from src.sgd.convert import number_to_roman
import os
import math

__author__ = 'kpaskov'

# --------------------- Convert Alias Evidence ---------------------
def make_alias_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Bioentityalias
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reflink as OldReflink
    from src.sgd.model.bud.feature import AliasFeature as OldAliasFeature
    from src.sgd.model.bud.general import DbxrefFeat as OldDbxrefFeat
    def alias_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
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
            alias_key = 'BIOENTITY', old_alias.alias_name, str(bioentity_id), old_alias.alias_type

            if old_alias.id in feat_alias_id_to_reflinks:
                for reflink in feat_alias_id_to_reflinks[old_alias.id]:
                    reference_id = reflink.reference_id
                    if alias_key in key_to_alias and reference_id in id_to_reference:
                        yield {'source': key_to_source['SGD'],
                               'reference': id_to_reference[reference_id],
                               'alias': key_to_alias[alias_key],
                               'date_created': reflink.date_created,
                               'created_by': reflink.created_by}
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
                            yield {'source': key_to_source[old_dbxref_feat.dbxref.source.replace('/', '-')],
                                   'reference': id_to_reference[reference_id],
                                   'alias': key_to_alias[alias_key],
                                   'date_created': reflink.date_created,
                                   'created_by': reflink.created_by}
                        else:
                            print 'Reference or alias not found: ' + str(reference_id) + ' ' + str(alias_key)

        bud_session.close()
        nex_session.close()
    return alias_evidence_starter

# --------------------- Binding Evidence ---------------------
def make_binding_evidence_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Experiment, Source
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.bioentity import Bioentity
    def binding_evidence_starter():
        nex_session = nex_session_maker()

        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Bioentity).all()])
        pubmed_to_reference = dict([(x.pubmed_id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for row in make_file_starter('src/sgd/convert/data/yetfasco_data.txt', delimeter=';')():
            expert_confidence = row[8][1:-1]
            if expert_confidence == 'High':
                bioent_key = (row[2][1:-1].upper(), 'LOCUS')
                experiment_key = create_format_name(row[9][1:-1])
                pubmed_id = int(row[10][1:-1])
                if bioent_key in key_to_bioentity and experiment_key in key_to_experiment:
                    yield {'source': key_to_source['YeTFaSCo'],
                           'reference': None if pubmed_id not in pubmed_to_reference else pubmed_to_reference[pubmed_id],
                           'experiment': key_to_experiment[experiment_key],
                           'locus': key_to_bioentity[bioent_key],
                           'total_score': row[6][1:-1],
                           'expert_confidence': expert_confidence,
                           'motif_id': int(row[3][1:-1])}
                else:
                    print 'Bioentity or experiment' + str(bioent_key) + ' ' + str(experiment_key)

        nex_session.close()
    return binding_evidence_starter

# --------------------- Convert Bioentity Evidence ---------------------
def make_bioentity_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Reflink as OldReflink
    from src.sgd.model.bud.feature import Annotation as OldAnnotation, FeatureProperty as OldFeatureProperty
    def bioentity_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])

        old_reflinks = bud_session.query(OldReflink).filter_by(tab_name='FEAT_ANNOTATION').all()
        feature_id_to_reflinks = dict()
        for reflink in old_reflinks:
            if reflink.primary_key in feature_id_to_reflinks:
                feature_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                feature_id_to_reflinks[reflink.primary_key] = [reflink]

        feature_property_id_to_reflinks = dict()
        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEAT_PROPERTY').all():
            if reflink.primary_key in feature_property_id_to_reflinks:
                feature_property_id_to_reflinks[reflink.primary_key].append(reflink)
            else:
                feature_property_id_to_reflinks[reflink.primary_key] = [reflink]

        for old_annotation in bud_session.query(OldAnnotation).all():
            bioentity_id = old_annotation.feature_id

            if bioentity_id in feature_id_to_reflinks:
                for reflink in feature_id_to_reflinks[bioentity_id]:
                    reference_id = reflink.reference_id
                    info_key = None
                    info_value = None
                    if reflink.col_name == 'QUALIFIER':
                        info_key = "Qualifier"
                        info_value = str(old_annotation.qualifier)
                    elif reflink.col_name == 'NAME_DESCRIPTION':
                        info_key = "Name Description"
                        info_value = str(old_annotation.name_description)
                    elif reflink.col_name == 'DESCRIPTION':
                        info_key = "Description"
                        info_value = str(old_annotation.description)
                    elif reflink.col_name == 'GENETIC_POSITION':
                        info_key = "Genetic Position"
                        info_value = str(old_annotation.genetic_position)
                    elif reflink.col_name == 'HEADLINE':
                        info_key = "Headline"
                        info_value = str(old_annotation.headline)
                    elif reflink.col_name == 'FEAT_ATTRIBUTE':
                        info_key = "Silenced Gene",
                        info_value = 'True'

                    if bioentity_id in id_to_bioentity and reference_id in id_to_reference and info_key is not None:
                        yield {'source': key_to_source['SGD'],
                               'reference': id_to_reference[reference_id],
                               'strain': key_to_strain['S288C'],
                               'bioentity': id_to_bioentity[bioentity_id],
                               'info_key': info_key,
                               'info_value': info_value,
                               'date_created': old_annotation.date_created,
                               'created_by': old_annotation.created_by}
                    else:
                        #print 'Could not find reference or bioentity or col_name: ' + str(bioentity_id) + ' ' + str(reference_id) + ' ' + reflink.col_name
                        yield None

        for reflink in bud_session.query(OldReflink).filter_by(tab_name='FEATURE').all():
            bioentity_id = reflink.primary_key
            reference_id = reflink.reference_id
            if bioentity_id in id_to_bioentity and reference_id in id_to_reference:
                bioentity = id_to_bioentity[bioentity_id]
                info_key = None
                info_value = None
                if reflink.col_name == 'GENE_NAME':
                    info_key = "Gene Name"
                    info_value = bioentity.gene_name
                elif reflink.col_name == 'FEATURE_NO':
                    info_key = '-'
                    info_value = '-'
                elif reflink.col_name == 'FEATURE_TYPE':
                    info_key = "Feature Type"
                    info_value = bioentity.locus_type

                if info_key is not None:
                    yield {'source': key_to_source['SGD'],
                           'reference': id_to_reference[reference_id],
                           'strain': key_to_strain['S288C'],
                           'bioentity': bioentity,
                           'info_key': info_key,
                           'info_value': info_value,
                           'date_created': reflink.date_created,
                           'created_by': reflink.created_by}
            else:
                #print 'Could not find reference or bioentity or col_name: ' + str(bioentity_id) + ' ' + str(reference_id) + ' ' + reflink.col_name
                yield None

        for feature_property in bud_session.query(OldFeatureProperty).all():
            bioentity_id = feature_property.feature_id

            if feature_property.id in feature_property_id_to_reflinks:
                for reflink in feature_property_id_to_reflinks[feature_property.id]:
                    reference_id = reflink.reference_id
                    if bioentity_id in id_to_bioentity and reference_id in id_to_reference:
                        yield {'source': key_to_source[feature_property.source],
                               'reference': id_to_reference[reference_id],
                               'strain': key_to_strain['S288C'],
                               'bioentity': id_to_bioentity[bioentity_id],
                               'info_key': feature_property.property_type,
                               'info_value': feature_property.property_value,
                               'date_created': feature_property.date_created,
                               'created_by': feature_property.created_by}
                    else:
                        #print 'Could not find reference or bioentity: ' + str(bioentity_id) + ' ' + str(reference_id)
                        yield None

        bud_session.close()
        nex_session.close()
    return bioentity_evidence_starter

# --------------------- Convert Domain Evidence ---------------------
def make_domain_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioitem import Domain
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.sequence import ProteinDetail, ProteinInfo
    def domain_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])
        id_to_bioentity = dict([(x.id, x) for x in key_to_bioentity.values()])
        key_to_domain = dict([(x.unique_key(), x) for x in nex_session.query(Domain).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        pubmed_id_to_reference = dict([(x.pubmed_id, x) for x in nex_session.query(Reference).all()])

        for row in make_file_starter('src/sgd/convert/data/domains.tab')():
            source_key = row[3].strip()
            start = row[6].strip()
            end = row[7].strip()
            evalue = row[8].strip()
            status = row[9].strip()
            date_of_run = datetime.strptime(row[10].strip(), "%d-%m-%Y").date()

            if source_key == 'Coils':
                source_key = '-'

            bioent_key = (row[0].strip(), 'LOCUS')
            domain_key = (create_format_name(row[4].strip()), 'DOMAIN')



            if status == 'T':
                if bioent_key in key_to_bioentity and domain_key in key_to_domain and source_key in key_to_source:
                    yield {
                        'source': key_to_source[source_key],
                        'strain': key_to_strain['S288C'],
                        'start': int(start),
                        'end': int(end),
                        'evalue': evalue,
                        'status': status,
                        'date_of_run': date_of_run,
                        'locus': key_to_bioentity[bioent_key],
                        'domain': key_to_domain[domain_key]}
                else:
                    print 'Bioentity or domain or source not found: ' + str(bioent_key) + ' ' + str(domain_key) + ' ' + str(source_key)
                    yield None

        for protein_detail in bud_session.query(ProteinDetail).options(joinedload('info')).all():
            bioentity_id = protein_detail.info.feature_id
            domain_key = None
            source = None
            if protein_detail.type == 'transmembrane domain':
                domain_key = ('predicted_transmembrane_domain', 'DOMAIN')
                source = key_to_source['TMHMM']
            elif protein_detail.type == 'signal peptide':
                domain_key = ('predicted_signal_peptide', 'DOMAIN')
                source = key_to_source['SignalP']

            if domain_key is not None:
                if bioentity_id in id_to_bioentity and domain_key in key_to_domain:
                    yield {'source': source,
                           'strain': key_to_strain['S288C'],
                           'start': int(protein_detail.min_coord),
                           'end': int(protein_detail.max_coord),
                           'locus': id_to_bioentity[bioentity_id],
                           'domain': key_to_domain[domain_key],
                           'date_created': protein_detail.date_created,
                           'created_by': protein_detail.created_by}
                else:
                    print 'Bioentity or domain not found: ' + str(bioentity_id) + ' ' + str(domain_key)
                    yield None

        bioentity_id_to_protein_length = dict([(x.feature_id, x.length) for x in bud_session.query(ProteinInfo).all()])

        for row in make_file_starter('src/sgd/convert/data/TF_family_class_accession04302013.txt')():
            bioent_key = (row[2].strip(), 'LOCUS')
            domain_key = (row[0], 'DOMAIN')
            pubmed_id = int(row[6].strip())

            if bioent_key in key_to_bioentity and domain_key in key_to_domain and pubmed_id in pubmed_id_to_reference:
                bioentity = key_to_bioentity[bioent_key]
                if bioentity.id in bioentity_id_to_protein_length:
                    yield {'source': key_to_source['JASPAR'],
                           'reference': pubmed_id_to_reference[pubmed_id],
                           'strain': key_to_strain['S288C'],
                           'start': 1,
                           'end': bioentity_id_to_protein_length[bioentity.id],
                           'status': 'T',
                           'locus': bioentity,
                           'domain': key_to_domain[domain_key]}
                else:
                    print 'Protein length not found: ' + str(bioent_key)
                    yield None
            else:
                print 'Bioentity or domain or reference not found: ' + str(bioent_key) + ' ' + str(domain_key) + ' ' + str(pubmed_id)
                yield None

        bud_session.close()
        nex_session.close()
    return domain_evidence_starter

# --------------------- Convert Domain Evidence ---------------------
def make_pathway_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioitem import Pathway
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.bud.general import DbxrefFeat
    def pathway_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        key_to_pathway = dict([(x.unique_key(), x) for x in nex_session.query(Pathway).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for dbxref_feat in bud_session.query(DbxrefFeat).filter(DbxrefFeat.dbxref.has(dbxref_type='Pathway ID')).all():
            yield {'source': key_to_source[dbxref_feat.dbxref.source],
                   'locus': id_to_bioentity[dbxref_feat.feature_id],
                   'pathway': key_to_pathway[(dbxref_feat.dbxref.dbxref_id, 'PATHWAY')],
                   'date_created': dbxref_feat.dbxref.date_created,
                   'created_by': dbxref_feat.dbxref.created_by}

        bud_session.close()
        nex_session.close()
    return pathway_evidence_starter

# --------------------- Convert ECnumber Evidence ---------------------
def make_ecnumber_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioconcept import ECNumber
    from src.sgd.model.bud.general import Dbxref
    def ecnumber_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        key_to_bioconcept = dict([(x.unique_key(), x) for x in nex_session.query(ECNumber).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for old_dbxref in make_db_starter(bud_session.query(Dbxref).filter(Dbxref.dbxref_type == 'EC number').options(joinedload(Dbxref.dbxref_feats)), 1000)():
            bioconcept_key = (old_dbxref.dbxref_id, 'EC_NUMBER')
            for dbxref_feat in old_dbxref.dbxref_feats:
                bioentity_id = dbxref_feat.feature_id

                if bioconcept_key in key_to_bioconcept and bioentity_id in id_to_bioentity:
                    yield {'source': key_to_source[old_dbxref.source],
                           'locus': id_to_bioentity[bioentity_id],
                           'ecnumber': key_to_bioconcept[bioconcept_key],
                           'date_created': old_dbxref.date_created,
                           'created_by': old_dbxref.created_by}
                else:
                    print 'Bioconcept or bioentity not found: ' + str(bioconcept_key) + ' ' + str(bioentity_id)

        bud_session.close()
        nex_session.close()
    return ecnumber_evidence_starter

# --------------------- Convert GO Evidence ---------------------
def make_go_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Experiment
    from src.sgd.model.nex.bioentity import Bioentity, Locus
    from src.sgd.model.nex.paragraph import Bioentityparagraph
    from src.sgd.model.nex.bioconcept import Bioconcept
    from src.sgd.model.nex.bioitem import Bioitem
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.go import GoFeature
    def go_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_bioconcept = dict([(x.unique_key(), x) for x in nex_session.query(Bioconcept).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioitem = dict([(x.unique_key(), x) for x in nex_session.query(Bioitem).all()])
        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        sgdid_to_bioentity = dict([(x.sgdid, x) for x in id_to_bioentity.values()])
        chebi_id_to_chemical = dict([(x.chebi_id, x) for x in key_to_bioitem.values() if x.class_type == 'CHEMICAL'])

        uniprot_id_to_bioentity = dict([(x.uniprotid, x) for x in id_to_bioentity.values()])
        pubmed_id_to_reference = dict([(str(x.pubmed_id), x) for x in id_to_reference.values()])

        term_id_to_role = dict()
        ancestor_name_to_role = {'catalytic activity': 'has substrate',
                                 'transport': 'transports',
                                 'transporter activity': 'transports',
                                 'binding': 'binds',
                                 'localization': 'localizes'}

        for ancestor_name, role in ancestor_name_to_role.iteritems():
            ancestor = nex_session.query(Bioconcept).filter_by(display_name=ancestor_name).first()
            children = [ancestor]
            while len(children) > 0:
                new_children = []
                for child in children:
                    term_id_to_role[child.id] = role
                    new_children.extend([x.child for x in child.children if x.relation_type == 'is a'])
                children = new_children

        evidence_key_to_gpad_conditions = dict(filter(None, [make_go_gpad_conditions(x, uniprot_id_to_bioentity, pubmed_id_to_reference, key_to_bioconcept, chebi_id_to_chemical, sgdid_to_bioentity, term_id_to_role) for x in make_file_starter('src/sgd/convert/data/gp_association.559292_sgd')()]))

        for old_go_feature in bud_session.query(GoFeature).options(joinedload(GoFeature.go_refs)).all():
            go_key = ('GO:' + str(old_go_feature.go.go_go_id).zfill(7), 'GO')
            if go_key[0] == 'GO:0008150':
                go_key = ('biological_process', 'GO')
            elif go_key[0] == 'GO:0003674':
                go_key = ('molecular_function', 'GO')
            elif go_key[0] == 'GO:0005575':
                go_key = ('cellular_component', 'GO')
            bioent_id = old_go_feature.feature_id
            source_key = old_go_feature.source

            for old_go_ref in old_go_feature.go_refs:
                reference_id = old_go_ref.reference_id
                if bioent_id in id_to_bioentity and go_key in key_to_bioconcept and reference_id in id_to_reference:
                    go = key_to_bioconcept[go_key]
                    go_evidence = old_go_feature.go_evidence

                    if old_go_ref.go_qualifier is not None:
                        qualifier = old_go_ref.go_qualifier.qualifier.replace('_', ' ')
                    else:
                        if go.go_aspect == 'biological process':
                            qualifier = 'involved in'
                        elif go.go_aspect == 'molecular function':
                            qualifier = 'enables'
                        elif go.go_aspect == 'cellular component':
                            qualifier = 'part of'
                        else:
                            qualifier = None

                    conditions = make_go_conditions(old_go_ref.goref_dbxrefs, sgdid_to_bioentity, key_to_bioconcept, key_to_bioitem)
                    evidence_key = 'GO', bioent_id, key_to_bioconcept[go_key].id, go_evidence, reference_id, None
                    if evidence_key in evidence_key_to_gpad_conditions:
                        conditions.extend(evidence_key_to_gpad_conditions[evidence_key])

                    key_to_condition = {}
                    for condition in conditions:
                        key_to_condition[condition.unique_key()] = condition

                    yield {'source': key_to_source[source_key],
                           'experiment': key_to_experiment[go_evidence],
                           'reference': id_to_reference[reference_id],
                           'locus': id_to_bioentity[bioent_id],
                           'go': go,
                           'go_evidence': go_evidence,
                           'annotation_type': old_go_feature.annotation_type,
                           'qualifier': qualifier,
                           'properties': key_to_condition.values(),
                           'date_created': old_go_ref.date_created if go_evidence != 'IEA' else old_go_feature.date_last_reviewed,
                           'created_by': old_go_ref.created_by}
                else:
                    print 'Could not find bioentity or bioconcept or reference: ' + str(bioent_id) + ' ' + str(go_key) + ' ' + str(reference_id)

        bud_session.close()
        nex_session.close()
    return go_evidence_starter

def make_go_conditions(old_dbxrefs, sgdid_to_bioentity, key_to_bioconcept, key_to_bioitem):
    from src.sgd.model.nex.evidence import Bioconceptproperty, Bioentityproperty, Bioitemproperty
    conditions = []
    for dbxrefref in old_dbxrefs:
        dbxref = dbxrefref.dbxref
        dbxref_type = dbxref.dbxref_type
        if dbxref_type == 'GOID':
            go_key = ('GO:' + str(int(dbxref.dbxref_id)).zfill(7), 'GO')
            if go_key in key_to_bioconcept:
                conditions.append(Bioconceptproperty({'role': dbxrefref.support_type, 'bioconcept': key_to_bioconcept[go_key]}))
            else:
                print 'Could not find bioconcept: ' + str(go_key)
        elif dbxref_type == 'EC number':
            ec_key = (dbxref.dbxref_id, 'EC_NUMBER')
            if ec_key in key_to_bioconcept:
                conditions.append(Bioconceptproperty({'role': dbxrefref.support_type, 'bioconcept': key_to_bioconcept[ec_key]}))
            else:
                print 'Could not find bioconcept: ' + str(ec_key)
        elif dbxref_type == 'DBID Primary':
            sgdid = dbxref.dbxref_id
            if sgdid in sgdid_to_bioentity:
                conditions.append(Bioentityproperty({'role': dbxrefref.support_type, 'bioentity': sgdid_to_bioentity[sgdid]}))
            else:
                print 'Could not find bioentity: ' + str(sgdid)
        elif dbxref_type == 'PANTHER' or dbxref_type == 'Prosite':
            domain_key = (dbxref.dbxref_id, 'DOMAIN')
            if domain_key in key_to_bioitem:
                conditions.append(Bioitemproperty({'role': dbxrefref.support_type, 'bioitem': key_to_bioitem[domain_key]}))
            else:
                #print 'Could not find bioitem: ' + str(domain_key)
                pass
        else:
            bioitem_key = (dbxref.dbxref_id, 'ORPHAN')
            if bioitem_key in key_to_bioitem:
                conditions.append(Bioitemproperty({'role': dbxrefref.support_type, 'bioitem': key_to_bioitem[bioitem_key]}))
            else:
                print 'Could not find bioitem: ' + str(bioitem_key)
    return conditions

#This is a hack - we need to figure out what we're doing with these relationships, but right now it's unclear.
condition_format_name_to_display_name = {'activated by':	                'activated by',
                                        'dependent on':	                    'dependent on',
                                        'during':	                        'during',
                                        'exists during':	                'during',
                                        'happens during':	                'during',
                                        'has part':	                        'has part',
                                        'has regulation_target':	        'regulates',
                                        'in presence_of':	                'in presence of',
                                        'independent of':	                'independent of',
                                        'inhibited by':	                    'inhibited by',
                                        'localization dependent on':	    'localization requires',
                                        'modified by':	                    'modified by',
                                        'not during':	                    'except during',
                                        'not exists during':	            'except during',
                                        'not happens during':	            'except during',
                                        'not occurs at':	                'not at',
                                        'not occurs in':	                'not in',
                                        'occurs at':	                    'at',
                                        'occurs in':	                    'in',
                                        'part of':	                        'part of',
                                        'requires direct regulator':	    'requires direct regulation by',
                                        'requires localization':	        'only when located at',
                                        'requires modification':	        'only with modification',
                                        'requires regulation by':	        'requires regulation by',
                                        'requires regulator':	            'requires',
                                        'requires sequence feature':	    'requires',
                                        'requires substance':	            'requires',
                                        'requires target sequence feature':	'requires feature in target',
                                        'stabilizes':	                    'stabilizes'}

def make_go_gpad_conditions(gpad, uniprot_id_to_bioentity, pubmed_id_to_reference, key_to_bioconcept,
                              chebi_id_to_chemical, sgdid_to_bioentity, term_id_to_role):
    from src.sgd.model.nex.evidence import Bioconceptproperty, Bioentityproperty, Chemicalproperty

    if len(gpad) > 1 and gpad[9] == 'SGD':
        go_key = ('GO:' + str(int(gpad[3][3:])).zfill(7), 'GO')
        uniprot_id = gpad[1]
        pubmed_id = gpad[4][5:]

        go_evidence = None
        for annotation_prop in gpad[11].split('|'):
            pieces = annotation_prop.split('=')
            if pieces[0] == 'go_evidence':
                go_evidence = pieces[1]

        if go_key in key_to_bioconcept and uniprot_id in uniprot_id_to_bioentity and pubmed_id in pubmed_id_to_reference:
            evidence_key = 'GO', uniprot_id_to_bioentity[uniprot_id].id, key_to_bioconcept[go_key].id, go_evidence, pubmed_id_to_reference[pubmed_id].id, None
            conditions = []

            for x in gpad[10].strip().split(','):
                for annotation_ext in x.split('|'):
                    if '(' in annotation_ext:
                        pieces = annotation_ext.split('(')
                        role = pieces[0].replace('_', ' ')
                        if role in condition_format_name_to_display_name:
                            role = condition_format_name_to_display_name[role]
                        value = pieces[1][:-1]

                        if value.startswith('GO:'):
                            go_key = ('GO:' + str(int(value[3:])).zfill(7), 'GO')
                            if go_key in key_to_bioconcept:
                                goterm = key_to_bioconcept[go_key]
                                if goterm.id in term_id_to_role:
                                    role = term_id_to_role[goterm.id]
                                conditions.append(Bioconceptproperty({'role': role, 'bioconcept': goterm}))
                            else:
                                print 'Could not find bioconcept: ' + str(go_key)
                        elif value.startswith('CHEBI:'):
                            chebi_id = value
                            if chebi_id in chebi_id_to_chemical:
                                conditions.append(Chemicalproperty({'role': role, 'bioitem': chebi_id_to_chemical[chebi_id]}))
                            else:
                                print 'Could not find chemical: ' + str(chebi_id)
                        elif value.startswith('SGD:'):
                            sgdid = value[4:]
                            if sgdid in sgdid_to_bioentity:
                                conditions.append(Bioentityproperty({'role': role, 'bioentity': sgdid_to_bioentity[sgdid]}))
                            else:
                                print 'Could not find bioentity: ' + str(sgdid)

                        elif value.startswith('UniProtKB:'):
                            uniprotid = value[10:]
                            if uniprotid in uniprot_id_to_bioentity:
                                conditions.append(Bioentityproperty({'role': role, 'bioentity': uniprot_id_to_bioentity[uniprotid]}))
                            else:
                                print 'Could not find bioentity: ' + str(uniprotid)

                        else:
                            print 'Annotation not handled: ' + str((role, value))
            return evidence_key, conditions
    return None

# bioentity_key_to_date = dict()
#     #Go
#     for gofeature in bud_session.query(GoFeature).all():
#         bioentity_key = (gofeature.feature.name, 'LOCUS')
#         if gofeature.annotation_type == 'manually curated' and bioentity_key not in bioentity_key_to_date:
#             bioentity_key_to_date[bioentity_key] = gofeature.date_last_reviewed
#
#     for bioentity_key, date_last_reviewed in bioentity_key_to_date.iteritems():
#         if bioentity_key in key_to_bioentity:
#             yield {
#                 'bioentity': key_to_bioentity[bioentity_key],
#                 'source': key_to_source['SGD'],
#                 'text': str(date_last_reviewed),
#                 'html': str(date_last_reviewed),
#                 'date_created': None,
#                 'created_by': None,
#                 'category': 'GODATE'
#             }
#         else:
#             #print 'Bioentity not found: ' + str(bioentity_key)
#             yield None


def make_go_slim_evidence_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.bioconcept import Go

    def go_slim_evidence_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        goid_to_go = dict([(x.go_id, x) for x in nex_session.query(Go).all()])
        sgdid_to_bioentity = dict([(x.sgdid, x) for x in nex_session.query(Bioentity).all()])

        for pieces in make_file_starter('src/sgd/convert/data/go_slim_mapping.tab.txt')():
            if len(pieces) >= 6:
                goid = pieces[5]
                sgdid = pieces[2]
                aspect = pieces[3]
                if goid in goid_to_go and sgdid in sgdid_to_bioentity:
                    yield {'source': key_to_source['SGD'],
                           'locus': sgdid_to_bioentity[sgdid],
                            'go': goid_to_go[goid],
                            'aspect': aspect}
                elif sgdid in sgdid_to_bioentity:
                    yield {'source': key_to_source['SGD'],
                           'locus': sgdid_to_bioentity[sgdid],
                           'aspect': aspect}
                else:
                    print 'Could not find bioentity or bioconcept: ' + sgdid + ' ' + goid

        nex_session.close()
    return go_slim_evidence_starter

# --------------------- History Evidence ---------------------
note_type_to_preface = {'Nomenclature history': 'Nomenclature', 'Nomenclature conflict': 'Nomenclature',
                        'Other': 'Other', 'Mapping': 'Mapping'}
def make_history_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.bud.general import Note
    from src.sgd.model.bud.reference import Reflink
    from src.sgd.model.nex.misc import Experiment, Source
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.bioentity import Locus
    def history_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        note_id_to_reference_ids = dict()
        for note_link in bud_session.query(Reflink).filter_by(tab_name='NOTE').all():
            if note_link.primary_key in note_id_to_reference_ids:
                note_id_to_reference_ids[note_link.primary_key].append(note_link.reference_id)
            else:
                note_id_to_reference_ids[note_link.primary_key] = [note_link.reference_id]

        for note in bud_session.query(Note).filter(Note.note_type.in_({'Alternative processing', 'Annotation change',
                                                                       'Mapping', 'Proposed annotation change', 'Proposed sequence change', 'Sequence change', 'Other'})).all():
            for note_feat in note.note_feats:
                bioentity_id = note_feat.primary_key
                if note_feat.tab_name == 'FEATURE':
                    if note.id in note_id_to_reference_ids:
                        for reference_id in note_id_to_reference_ids[note.id]:
                            if reference_id in id_to_reference and bioentity_id in id_to_bioentity:
                                yield {'source': key_to_source['SGD'],
                                       'reference': id_to_reference[reference_id],
                                       'locus': id_to_bioentity[bioentity_id],
                                       'category': note.note_type,
                                       'history_type': 'SEQUENCE',
                                       'note': ('' if note.note_type not in note_type_to_preface else '<strong>' + note_type_to_preface[note.note_type] + ':</strong> ') + note.note,
                                       'date_created': note_feat.date_created,
                                       'created_by': note_feat.created_by
                                       }
                            else:
                                #print 'Bioentity or reference not found: ' + str(bioentity_id) + ', ' + str(reference_id)
                                yield None
                    else:
                        if bioentity_id in id_to_bioentity:
                            yield {'source': key_to_source['SGD'],
                                    'locus': id_to_bioentity[bioentity_id],
                                    'category': note.note_type,
                                    'history_type': 'SEQUENCE',
                                    'note': ('' if note.note_type not in note_type_to_preface else '<strong>' + note_type_to_preface[note.note_type] + ':</strong> ') + note.note,
                                    'date_created': note_feat.date_created,
                                    'created_by': note_feat.created_by
                                    }
                        else:
                            # print 'Bioentity not found: ' + str(bioentity_id)
                            yield None

        for note in bud_session.query(Note).filter(Note.note_type.in_({'Nomenclature conflict', 'Nomenclature history',
                                                                       'Reserved Name Note', 'Other'})).all():
            for note_feat in note.note_feats:
                bioentity_id = note_feat.primary_key
                if note_feat.tab_name == 'FEATURE':
                    if note.id in note_id_to_reference_ids:
                        for reference_id in note_id_to_reference_ids[note.id]:
                            if reference_id in id_to_reference and bioentity_id in id_to_bioentity:
                                yield {'source': key_to_source['SGD'],
                                       'reference': id_to_reference[reference_id],
                                       'locus': id_to_bioentity[bioentity_id],
                                       'category': note.note_type,
                                       'history_type': 'LSP',
                                       'note': ('' if note.note_type not in note_type_to_preface else '<strong>' + note_type_to_preface[note.note_type] + ':</strong> ') + note.note,
                                       'date_created': note_feat.date_created,
                                       'created_by': note_feat.created_by
                                       }
                            else:
                                #print 'Bioentity or reference not found: ' + str(bioentity_id) + ', ' + str(reference_id)
                                yield None
                    else:
                        if bioentity_id in id_to_bioentity:
                            yield {'source': key_to_source['SGD'],
                                    'locus': id_to_bioentity[bioentity_id],
                                    'category': note.note_type,
                                    'history_type': 'LSP',
                                    'note': ('' if note.note_type not in note_type_to_preface else '<strong>' + note_type_to_preface[note.note_type] + ':</strong> ') + note.note,
                                    'date_created': note_feat.date_created,
                                    'created_by': note_feat.created_by
                                    }
                        else:
                            #print 'Bioentity not found: ' + str(bioentity_id)
                            yield None

        for bioentity in id_to_bioentity.values():
            for quality in bioentity.qualities:
                if quality.display_name == 'Gene Name':
                    for quality_reference in quality.quality_references:
                        yield {'source': key_to_source['SGD'],
                                   'reference': quality_reference.reference,
                                   'locus': bioentity,
                                   'category': 'Nomenclature',
                                   'history_type': 'LSP',
                                   'note': '<strong>Name:</strong> ' + bioentity.display_name,
                                   'date_created': datetime(quality_reference.reference.year, 1, 1),
                                   'created_by': None
                                }

            for alias in bioentity.aliases:
                if alias.category == 'Alias' or alias.category == 'Gene Product':
                    for alias_reference in alias.alias_references:
                        yield {'source': key_to_source['SGD'],
                                   'reference': alias_reference.reference,
                                   'locus': bioentity,
                                   'category': 'Nomenclature',
                                   'history_type': 'LSP',
                                   'note': '<strong>Name:</strong> ' + alias.display_name,
                                   'date_created': datetime(alias_reference.reference.year, 1, 1),
                                   'created_by': None
                                }
            if bioentity.reserved_name is not None:
                yield {'source': key_to_source['SGD'],
                               'reference': bioentity.reserved_name.reference,
                               'locus': bioentity,
                               'category': 'Nomenclature',
                               'history_type': 'LSP',
                               'note': '<strong>Reserved Name:</strong> ' + bioentity.reserved_name.display_name + ' (Reserved from ' + str(bioentity.reserved_name.reservation_date) + ' - ' + str(bioentity.reserved_name.expiration_date) + ')',
                               'date_created': bioentity.reserved_name.date_created,
                               'created_by': bioentity.reserved_name.created_by
                            }


        bud_session.close()
        nex_session.close()
    return history_evidence_starter

# --------------------- Convert Interaction Evidence ---------------------
def make_interaction_evidence_starter(bud_session_maker, nex_session_maker, interaction_type):
    from src.sgd.model.nex.misc import Experiment, Source
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.bioconcept import Phenotype, create_phenotype_format_name
    from src.sgd.model.bud.interaction import Interaction
    def interaction_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        key_to_phenotype = dict([(x.unique_key(), x) for x in nex_session.query(Phenotype).all()])
        id_to_bioentities = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for bud_obj in make_db_starter(bud_session.query(Interaction).filter_by(interaction_type=interaction_type), 1000)():
            reference_ids = bud_obj.reference_ids
            if len(reference_ids) != 1:
                print 'Too many references'
            reference_id = reference_ids[0]

            if bud_obj.interaction_features[0].feature_id < bud_obj.interaction_features[1].feature_id:
                bioent1_id = bud_obj.interaction_features[0].feature_id
                bioent2_id = bud_obj.interaction_features[1].feature_id
                bait_hit = bud_obj.interaction_features[0].action + '-' + bud_obj.interaction_features[1].action
            else:
                bioent1_id = bud_obj.interaction_features[1].feature_id
                bioent2_id = bud_obj.interaction_features[0].feature_id
                bait_hit = bud_obj.interaction_features[1].action + '-' + bud_obj.interaction_features[0].action

            experiment_key = create_format_name(bud_obj.experiment_type)

            if reference_id in id_to_reference and bioent1_id in id_to_bioentities and bioent2_id in id_to_bioentities and experiment_key in key_to_experiment:
                mutant_type = None
                phenotype = None
                phenotypes = bud_obj.interaction_phenotypes
                if len(phenotypes) == 1:
                    phenotype_key = (create_phenotype_format_name(phenotypes[0].observable, phenotypes[0].qualifier), 'PHENOTYPE')
                    if phenotype_key in key_to_phenotype:
                        phenotype = key_to_phenotype[phenotype_key]
                        mutant_type = phenotypes[0].mutant_type
                    else:
                        print 'Phenotype not found: ' + str(phenotype_key)
                elif len(phenotypes) > 1:
                    print 'Too many phenotypes'

                yield {'source': key_to_source[bud_obj.source],
                        'reference': id_to_reference[reference_id],
                        'experiment': key_to_experiment[experiment_key],
                        'locus1': id_to_bioentities[bioent1_id],
                        'locus2': id_to_bioentities[bioent2_id],
                        'phenotype': phenotype,
                        'mutant_type': mutant_type,
                        'modification': bud_obj.modification,
                        'annotation_type': bud_obj.annotation_type,
                        'bait_hit': bait_hit,
                        'note': bud_obj.interaction_references[0].note,
                        'date_created': bud_obj.date_created,
                        'created_by': bud_obj.created_by}
        bud_session.close()
        nex_session.close()
    return interaction_evidence_starter

# --------------------- Convert Literature Evidence ---------------------
def make_literature_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Litguide
    def literature_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for litguide in make_db_starter(bud_session.query(Litguide).filter(Litguide.topic.in_({'Additional Literature', 'Primary Literature', 'Omics', 'Reviews'})).options(joinedload(Litguide.litguide_features)), 1000)():
            reference_id = litguide.reference_id

            for litguide_feature in litguide.litguide_features:
                bioentity_id = litguide_feature.feature_id
                if reference_id in id_to_reference and bioentity_id in id_to_bioentity:
                    yield {'source': key_to_source['SGD'],
                           'reference': id_to_reference[reference_id],
                           'locus': id_to_bioentity[bioentity_id],
                           'topic': litguide.topic,
                           'date_created': litguide_feature.date_created,
                           'created_by': litguide_feature.created_by}
                else:
                    if reference_id not in id_to_reference:
                        print 'Reference not found: ' + str(bioentity_id) + ' ' + str(reference_id)

        bud_session.close()
        nex_session.close()

    return literature_evidence_starter

# --------------------- Convert Archived Literature Evidence ---------------------
def make_archive_literature_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.reference import Litguide
    def archive_literature_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        for litguide in make_db_starter(bud_session.query(Litguide).options(joinedload(Litguide.litguide_features)), 1000)():
            reference_id = litguide.reference_id

            if litguide.topic not in {'Additional Literature', 'Primary Literature', 'Omics', 'Reviews'}:
                if len(litguide.litguide_features) > 0:
                    for litguide_feature in litguide.litguide_features:
                        bioentity_id = litguide_feature.feature_id
                        if reference_id in id_to_reference and bioentity_id in id_to_bioentity:
                            yield {'source': key_to_source['SGD'],
                                       'reference': id_to_reference[reference_id],
                                       'locus': id_to_bioentity[bioentity_id],
                                       'topic': litguide.topic,
                                       'date_created': litguide_feature.date_created,
                                       'created_by': litguide_feature.created_by}
                        else:
                            print 'Bioentity or reference not found: ' + str(bioentity_id) + ' ' + str(reference_id)
                else:
                    if reference_id in id_to_reference:
                        yield {'source': key_to_source['SGD'],
                               'reference': id_to_reference[reference_id],
                               'topic': litguide.topic,
                               'date_created': litguide.date_created,
                               'created_by': litguide.created_by}
                    else:
                            print 'Reference not found: ' + str(reference_id)

        bud_session.close()
        nex_session.close()

    return archive_literature_evidence_starter

# --------------------- Convert Phenotype Evidence ---------------------
def make_phenotype_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Experiment, Source, Strain
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.bioconcept import Phenotype, create_phenotype_format_name
    from src.sgd.model.nex.bioitem import Bioitem
    from src.sgd.model.bud.phenotype import PhenotypeFeature
    from src.sgd.model.bud.reference import Reflink
    def phenotype_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        key_to_phenotype = dict([(x.unique_key(), x) for x in nex_session.query(Phenotype).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])
        key_to_bioitem = dict([(x.unique_key(), x) for x in nex_session.query(Bioitem).all()])
        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])

        key_to_reflinks = dict()
        for old_reflink in bud_session.query(Reflink).all():
            reflink_key = (old_reflink.col_name, old_reflink.primary_key)
            if reflink_key in key_to_reflinks:
                key_to_reflinks[reflink_key].append(old_reflink)
            else:
                key_to_reflinks[reflink_key] = [old_reflink]

        for old_phenotype_feature in make_db_starter(bud_session.query(PhenotypeFeature).options(joinedload('experiment'), joinedload('phenotype')), 1000)():
            reference_ids = [] if ('PHENO_ANNOTATION_NO', old_phenotype_feature.id) not in key_to_reflinks else [x.reference_id for x in key_to_reflinks[('PHENO_ANNOTATION_NO', old_phenotype_feature.id)]]
            bioentity_id = old_phenotype_feature.feature_id
            experiment_key = create_format_name(old_phenotype_feature.experiment_type)
            source_key = old_phenotype_feature.source

            observable = old_phenotype_feature.observable
            qualifier = old_phenotype_feature.qualifier
            if observable == 'chemical compound accumulation' or observable == 'chemical compound excretion' or observable == 'resistance to chemicals':
                chemical = ' and '.join([x[0] for x in old_phenotype_feature.experiment.chemicals])
                if observable == 'resistance to chemicals':
                    observable = observable.replace('chemicals', chemical)
                else:
                    observable = observable.replace('chemical compound', chemical)
            phenotype_key = (create_phenotype_format_name(observable.lower(), qualifier), 'PHENOTYPE')

            strain_key = None
            note = None
            strain_details = None
            experiment_details = None
            conditions = []

            old_experiment = old_phenotype_feature.experiment
            if old_experiment is not None:
                if len(old_experiment.details):
                    note = '; '.join([a if b is None else a + ': ' + b for (a, b) in old_experiment.details])
                strain_details = None if old_experiment.strain is None else old_experiment.strain[1]
                experiment_details = None if old_experiment.experiment_comment is None else old_experiment.experiment_comment
                conditions = make_phenotype_conditions(old_experiment, key_to_bioitem)
                #Get strain
                if old_experiment.strain != None:
                    strain_key = old_experiment.strain[0]

            if strain_key == 'CEN.PK':
                strain_key = 'CENPK'

            for reference_id in reference_ids:
                if reference_id in id_to_reference and bioentity_id in id_to_bioentity and \
                                experiment_key in key_to_experiment and (strain_key is None or strain_key in key_to_strain) and \
                                source_key in key_to_source and phenotype_key in key_to_phenotype:
                    mutant_type = old_phenotype_feature.mutant_type
                    yield {'source': key_to_source[source_key],
                           'reference': id_to_reference[reference_id],
                           'strain': None if strain_key is None else key_to_strain[strain_key],
                           'experiment': key_to_experiment[experiment_key],
                           'note': note,
                           'locus': id_to_bioentity[bioentity_id],
                           'phenotype': key_to_phenotype[phenotype_key],
                           'mutant_type': mutant_type,
                           'strain_details': strain_details,
                           'experiment_details': experiment_details,
                           'properties': conditions,
                           'date_created': old_phenotype_feature.date_created,
                           'created_by': old_phenotype_feature.created_by}
                else:
                    print 'Reference or bioentity or experiment or strain or source or phenotype not found: ' + str(reference_id) + ' ' + \
                          str(bioentity_id) + ' ' + str(experiment_key) + ' ' + str(strain_key) + ' ' + str(source_key) + ' ' + str(phenotype_key)
        bud_session.close()
        nex_session.close()
    return phenotype_evidence_starter

def make_phenotype_conditions(old_experiment, key_to_bioitem):
    from src.sgd.model.nex.evidence import Bioitemproperty, Chemicalproperty, Generalproperty
    conditions = []
    #Get reporter
    if old_experiment.reporter is not None:
        reporter_key = (create_format_name(old_experiment.reporter[0]), 'ORPHAN')
        if reporter_key in key_to_bioitem:
            conditions.append(Bioitemproperty({'note': old_experiment.reporter[1], 'role': 'Reporter', 'bioitem': key_to_bioitem[reporter_key]}))
        else:
            print 'Reporter not found: ' + str(reporter_key)

    #Get allele
    if old_experiment.allele is not None:
        allele_key = (create_format_name(old_experiment.allele[0]), 'ALLELE')
        if allele_key in key_to_bioitem:
            conditions.append(Bioitemproperty({'note': old_experiment.allele[1], 'role': 'Allele', 'bioitem': key_to_bioitem[allele_key]}))
        else:
            print 'Allele not found: ' + str(allele_key)

    #Get chemicals
    for (a, b) in old_experiment.chemicals:
        chemical_key = (create_format_name(a)[:95], 'CHEMICAL')
        if chemical_key in key_to_bioitem:
            chemical_note = None
            amount = None
            if b is not None and contains_digits(b):
                amount = b
            else:
                chemical_note = b
            conditions.append(Chemicalproperty({'note': chemical_note, 'concentration': amount, 'bioitem': key_to_bioitem[chemical_key]}))
        else:
            print 'Chemical not found: ' + str(chemical_key)

    #Get other conditions
    for (a, b) in old_experiment.condition:
        conditions.append(Generalproperty({'note': a if b is None else a + ': ' + b}))
    return conditions

def make_phosphorylation_evidence_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.evidence import Generalproperty, Bioentityproperty
    def phosphorylation_evidence_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Bioentity).all()])

        for row in make_file_starter('src/sgd/convert/data/phosphosites.txt')():
            if len(row) == 19:
                bioentity_key = (row[0], 'LOCUS')

                conditions = {}

                site_functions = row[7]
                if site_functions != '-':
                    for site_function in site_functions.split('|'):
                        condition = Generalproperty({'note': site_function.capitalize()})
                        conditions[condition.unique_key()] = condition

                kinases = row[9]
                if kinases != '-':
                    for kinase in kinases.split('|'):
                        bioent_key = (kinase, 'LOCUS')
                        if bioent_key in key_to_bioentity:
                            condition = Bioentityproperty({'role': 'Kinase', 'bioentity': key_to_bioentity[bioent_key]})
                            conditions[condition.unique_key()] = condition
                        else:
                            print 'Bioentity not found: ' + str(bioent_key)

                if bioentity_key in key_to_bioentity:
                    yield {'source': key_to_source['PhosphoGRID'],
                           'locus': key_to_bioentity[bioentity_key],
                           'site_index': int(row[2][1:]),
                           'site_residue': row[2][0],
                           'properties': conditions.values()}
                else:
                    print 'Bioentity not found: ' + str(bioentity_key)

        nex_session.close()
    return phosphorylation_evidence_starter

def make_posttranslational_evidence_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.evidence import Generalproperty, Bioentityproperty
    def posttranslational_evidence_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Bioentity).all()])
        pmid_to_reference = dict([(x.pubmed_id, x) for x in nex_session.query(Reference).all()])

        #Phosphorylation
        for row in make_file_starter('src/sgd/convert/data/phosphosites.txt')():
            if len(row) == 19:
                bioentity_key = (row[0], 'LOCUS')

                conditions = {}

                site_functions = row[7]
                if site_functions != '-':
                    for site_function in site_functions.split('|'):
                        condition = Generalproperty({'note': site_function.capitalize()})
                        conditions[condition.unique_key()] = condition

                kinases = row[9]
                if kinases != '-':
                    for kinase in kinases.split('|'):
                        bioent_key = (kinase, 'LOCUS')
                        if bioent_key in key_to_bioentity:
                            condition = Bioentityproperty({'role': 'Kinase', 'bioentity': key_to_bioentity[bioent_key]})
                            conditions[condition.unique_key()] = condition
                        else:
                            print 'Bioentity not found: ' + str(bioent_key)

                if bioentity_key in key_to_bioentity:
                    yield {'source': key_to_source['PhosphoGRID'],
                           'locus': key_to_bioentity[bioentity_key],
                           'site_index': int(row[2][1:]),
                           'site_residue': row[2][0],
                           'type': 'phosphorylation',
                           'properties': conditions.values()}
                else:
                    print 'Bioentity not found: ' + str(bioentity_key)

        #Other sites
        file_names = ['src/sgd/convert/data/methylationSitesPMID25109467.txt',
                      'src/sgd/convert/data/ubiquitinationSites090314.txt',
                      'src/sgd/convert/data/phosphorylationUbiquitinationPMID23749301.txt',
                      'src/sgd/convert/data/succinylationAcetylation090914.txt']

        for file_name in file_names:
            print file_name
            f = open(file_name, 'rU')
            header = True
            for line in f:
                if header:
                    header = False
                else:
                    pieces = line.split('\t')
                    bioentity_key = (pieces[0], 'LOCUS')
                    site = pieces[1].strip()
                    site_residue = site[0]
                    site_index = int(site[1:])
                    site_functions = pieces[2]
                    modification_type = pieces[3]
                    modifier = pieces[4]
                    source_key = pieces[5]
                    pmid = int(pieces[6].replace('PMID:', ''))

                    if modifier is not '':
                        print modifier
                    if site_functions is not '':
                        print site_functions

                    if bioentity_key in key_to_bioentity and source_key in key_to_source and pmid in pmid_to_reference:
                        yield {
                           'source': key_to_source[source_key],
                           'locus': key_to_bioentity[bioentity_key],
                           'site_index': site_index,
                           'site_residue': site_residue,
                           'type': modification_type,
                           'reference': pmid_to_reference[pmid],
                           'properties': []
                        }
                    else:
                        print 'Bioentity or source or pmid not found: ' + str(bioentity_key) + ' ' + str(source_key) + ' ' + str(pmid)

            f.close()


        nex_session.close()
    return posttranslational_evidence_starter

def get_phosphorylation_pubmed_ids():
    pubmed_ids = set()
    for row in make_file_starter('src/sgd/convert/data/phosphosites.txt')():
        if len(row) >= 16:
            site_evidence_pubmed_ids = row[4]
            site_conditions_pubmed_ids = row[6]
            site_functions_pubmed_ids = row[8]
            kinase_evidence_pubmed_ids = row[12]
            phosphotases_evidence_pubmed_ids = row[16]

            if site_evidence_pubmed_ids != '-':
                pubmed_ids.update(get_pubmed_ids(site_evidence_pubmed_ids))
            if site_conditions_pubmed_ids != '-':
                pubmed_ids.update(get_pubmed_ids(site_conditions_pubmed_ids))
            if site_functions_pubmed_ids != '-':
                pubmed_ids.update(get_pubmed_ids(site_functions_pubmed_ids))
            if kinase_evidence_pubmed_ids != '-':
                pubmed_ids.update(get_pubmed_ids(kinase_evidence_pubmed_ids))
            if phosphotases_evidence_pubmed_ids != '-':
                pubmed_ids.update(get_pubmed_ids(phosphotases_evidence_pubmed_ids))
    print sorted(pubmed_ids)

def get_pubmed_ids(entry):
    first_round = [x.strip() for x in entry.split('|')]
    second_round = []
    for pmid in first_round:
        if len(pmid) == 6  or len(pmid) == 7 or len(pmid) == 8:
            second_round.append(pmid)
        elif len(pmid) == 16:
            second_round.append(pmid[0:8])
            second_round.append(pmid[8:16])
        else:
            print pmid
    return second_round


# --------------------- Convert Protein Experiment Evidence ---------------------
def make_protein_experiment_evidence_starter(bud_session_maker, nex_session_maker):
    from src.sgd.model.nex.misc import Source, Experiment
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.bud.sequence import ProteinDetail
    from src.sgd.model.bud.reference import Reflink
    def protein_experiment_evidence_starter():
        bud_session = bud_session_maker()
        nex_session = nex_session_maker()

        id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Locus).all()])
        id_to_reference = dict([(x.id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])

        protein_detail_id_to_reference = dict([(x.primary_key, x.reference_id) for x in bud_session.query(Reflink).filter(Reflink.tab_name == 'PROTEIN_DETAIL').all()])

        for old_protein_detail in bud_session.query(ProteinDetail).filter(ProteinDetail.group == 'molecules/cell').options(joinedload(ProteinDetail.info)).all():
            reference_id = protein_detail_id_to_reference[old_protein_detail.id]
            bioentity_id = old_protein_detail.info.feature_id
            if reference_id in id_to_reference and bioentity_id in id_to_bioentity:
                yield {'source': key_to_source['SGD'],
                       'reference': id_to_reference[reference_id],
                       'experiment': key_to_experiment['protein_abundance'],
                       'locus': id_to_bioentity[bioentity_id],
                       'data_value': old_protein_detail.value,
                       'data_unit': old_protein_detail.group,
                       'date_created': old_protein_detail.date_created,
                       'created_by': old_protein_detail.created_by}
            else:
                print 'Reference or bioentity not found: ' + str(reference_id) + ' ' + str(bioentity_id)

        bud_session.close()
        nex_session.close()
    return protein_experiment_evidence_starter

# --------------------- Regulation Evidence ---------------------
def make_regulation_evidence_starter(nex_session_maker):
    from src.sgd.model.nex.misc import Source, Experiment, Strain
    from src.sgd.model.nex.bioentity import Locus
    from src.sgd.model.nex.reference import Reference

    def regulation_evidence_starter():
        nex_session = nex_session_maker()

        key_to_experiment = dict([(x.unique_key(), x) for x in nex_session.query(Experiment).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])
        pubmed_to_reference = dict([(x.pubmed_id, x) for x in nex_session.query(Reference).all()])
        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

        header = False
        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Venters_Macisaac_Hu05-12-2014_regulator_lines')():
            if header:
                header = False
            else:
                bioent1_key = (row[1].strip(), 'LOCUS')
                bioent2_key = (row[3].strip(), 'LOCUS')
                experiment_format_name = create_format_name(row[4].strip())
                experiment_eco_id = row[5].strip()
                direction = None if row[7] == '' else row[7]
                pvalue = None if row[8] == '' else row[8]
                fdr = None if row[9] == '' else row[9]
                pubmed_id = int(row[10].strip())
                source_key = row[11].strip()
                strain_key = None if row[12].strip() == '' else row[12].strip()
                strain_background = None if row[13].strip() == '' else row[13].strip()


                if strain_key == 'CEN.PK':
                    strain_key = 'CENPK'

                if bioent1_key in key_to_bioentity and bioent2_key in key_to_bioentity and (strain_key is None or strain_key in key_to_strain) and \
                                pubmed_id in pubmed_to_reference and source_key in key_to_source and \
                    (experiment_format_name in key_to_experiment or experiment_eco_id in key_to_experiment):
                    conditions = []
                    condition_value = row[6].strip()
                    construct = None
                    assay = None
                    if condition_value != '':
                        from src.sgd.model.nex.evidence import Generalproperty
                        condition_value = condition_value.replace('??', "\00b5")
                        if condition_value.startswith('"') and condition_value.endswith('"'):
                            condition_value = condition_value[1:-1]
                        condition_values = condition_value.split(';')
                        conditions.append(Generalproperty({'note': condition_values[0] + '; ' + condition_values[3]}))
                        construct = condition_values[2]
                        assay = condition_values[1]

                    yield {'source': key_to_source[source_key],
                           'reference': pubmed_to_reference[pubmed_id],
                           'strain': None if strain_key is None or strain_key not in key_to_strain else key_to_strain[strain_key],
                           'experiment': key_to_experiment[experiment_format_name] if experiment_format_name in key_to_experiment else key_to_experiment[experiment_eco_id],
                           'locus1': key_to_bioentity[bioent1_key],
                           'locus2': key_to_bioentity[bioent2_key],
                           'direction': direction,
                           'pvalue': pvalue,
                           'fdr': fdr,
                           'construct': strain_background if strain_background is not None else construct,
                           'assay': assay,
                           'properties': conditions}
                else:
                    print 'Bioentity or strain or reference or source or experiment not found: ' + str(bioent1_key) + ' ' + \
                          str(bioent2_key) + ' ' + experiment_eco_id + ' ' + experiment_format_name + ' ' + str(strain_key) + ' ' + str(pubmed_id) + ' ' + str(source_key)

        header = True
        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/SGD_data_05_14_2014')():
            if header:
                header = False
            else:
                bioent1_key = (row[1].strip(), 'LOCUS')
                bioent2_key = (row[3].strip(), 'LOCUS')
                experiment_format_name = create_format_name(row[4].strip())
                experiment_eco_id = row[5].strip()
                direction = None if row[7] == '' else row[7]
                pvalue = None if row[8] == '' else row[8]
                fdr = None if row[9] == '' else row[9]
                pubmed_id = int(row[10].strip())
                source_key = row[11].strip()
                strain_key = None if row[12].strip() == '' else row[12].strip()
                strain_background = None if row[13].strip() == '' else row[13].strip()

                if strain_key == 'CEN.PK':
                    strain_key = 'CENPK'

                if bioent1_key in key_to_bioentity and bioent2_key in key_to_bioentity and (strain_key is None or strain_key in key_to_strain) and \
                                pubmed_id in pubmed_to_reference and source_key in key_to_source and \
                    (experiment_format_name in key_to_experiment or experiment_eco_id in key_to_experiment):
                    conditions = []
                    condition_value = row[6].strip()
                    if condition_value != '""':
                        from src.sgd.model.nex.evidence import Generalproperty
                        condition_value = condition_value.replace('??', "\00b5")
                        if condition_value.startswith('"') and condition_value.endswith('"'):
                            condition_value = condition_value[1:-1]
                        conditions.append(Generalproperty({'note': condition_value}))

                    yield {'source': key_to_source[source_key],
                           'reference': pubmed_to_reference[pubmed_id],
                           'strain': None if strain_key is None or strain_key not in key_to_strain else key_to_strain[strain_key],
                           'experiment': key_to_experiment[experiment_format_name] if experiment_format_name in key_to_experiment else key_to_experiment[experiment_eco_id],
                           'locus1': key_to_bioentity[bioent1_key],
                           'locus2': key_to_bioentity[bioent2_key],
                           'direction': direction,
                           'pvalue': pvalue,
                           'fdr': fdr,
                           'construct': strain_background,
                           'properties': conditions}
                else:
                    print 'Bioentity or strain or reference or source or experiment not found: ' + str(bioent1_key) + ' ' + \
                          str(bioent2_key) + ' ' + experiment_eco_id + ' ' + experiment_format_name + ' ' + str(strain_key) + ' ' + str(pubmed_id) + ' ' + str(source_key)

        header = False
        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Madhani_fixed')():
            if header:
                header = False
            else:
                if len(row) >= 10:
                    bioent1_key = (row[1].strip(), 'LOCUS')
                    bioent2_key = (row[3].strip(), 'LOCUS')
                    experiment_format_name = create_format_name(row[5].strip())
                    experiment_eco_id = row[4].strip()
                    direction = None if row[7] == '' else row[7]
                    pvalue = None if row[8] == '' else row[8]
                    fdr = None if row[9] == '' else row[9]
                    pubmed_id = int(row[10].strip())
                    source_key = row[11].strip()
                    strain_key = None if row[12].strip() == '' else row[12].strip()
                    strain_background = None if row[13].strip() == '' else row[13].strip()

                    if strain_key == 'CEN.PK':
                        strain_key = 'CENPK'

                    if bioent1_key in key_to_bioentity and bioent2_key in key_to_bioentity and (strain_key is None or strain_key in key_to_strain) and \
                                    pubmed_id in pubmed_to_reference and source_key in key_to_source and \
                        (experiment_format_name in key_to_experiment or experiment_eco_id in key_to_experiment):
                        conditions = []
                        condition_value = row[6].strip()
                        if condition_value != '""':
                            from src.sgd.model.nex.evidence import Generalproperty
                            condition_value = condition_value.replace('??', "\00b5")
                            if condition_value.startswith('"') and condition_value.endswith('"'):
                                condition_value = condition_value[1:-1]
                            conditions.append(Generalproperty({'note': condition_value}))

                        yield {'source': key_to_source[source_key],
                               'reference': pubmed_to_reference[pubmed_id],
                               'strain': None if strain_key is None or strain_key not in key_to_strain else key_to_strain[strain_key],
                               'experiment': key_to_experiment[experiment_format_name] if experiment_format_name in key_to_experiment else key_to_experiment[experiment_eco_id],
                               'locus1': key_to_bioentity[bioent1_key],
                               'locus2': key_to_bioentity[bioent2_key],
                               'direction': direction,
                               'pvalue': pvalue,
                               'fdr': fdr,
                               'construct': strain_background,
                               'properties': conditions}
                    else:
                        print 'Bioentity or strain or reference or source or experiment not found: ' + str(bioent1_key) + ' ' + \
                              str(bioent2_key) + ' ' + experiment_eco_id + ' ' + experiment_format_name + ' ' + str(strain_key) + ' ' + str(pubmed_id) + ' ' + str(source_key)

        header = False
        for row in make_file_starter('src/sgd/convert/data/2014-05-15_reg_data/Pimentel_PMID22616008.txt')():
            if header:
                header = False
            else:
                if len(row) >= 10:
                    bioent1_key = (row[1].strip(), 'LOCUS')
                    bioent2_key = (row[3].strip(), 'LOCUS')
                    experiment_format_name = create_format_name(row[4].strip())
                    experiment_eco_id = row[5].strip()
                    direction = None if row[7] == '' else row[7]
                    pvalue = None if row[8] == '' else row[8]
                    fdr = None if row[9] == '' else row[9]
                    pubmed_id = int(row[10].strip())
                    source_key = row[11].strip()
                    strain_key = None if row[12].strip() == '' else row[12].strip()
                    strain_background = None if row[13].strip() == '' else row[13].strip()

                    if strain_key == 'CEN.PK':
                        strain_key = 'CENPK'

                    if bioent1_key in key_to_bioentity and bioent2_key in key_to_bioentity and (strain_key is None or strain_key in key_to_strain) and \
                                    pubmed_id in pubmed_to_reference and source_key in key_to_source and \
                        (experiment_format_name in key_to_experiment or experiment_eco_id in key_to_experiment):
                        conditions = []
                        condition_value = row[6].strip()
                        if condition_value != '""':
                            from src.sgd.model.nex.evidence import Generalproperty
                            condition_value = condition_value.replace('??', "\00b5")
                            if condition_value.startswith('"') and condition_value.endswith('"'):
                                condition_value = condition_value[1:-1]
                            conditions.append(Generalproperty({'note': condition_value}))

                        yield {'source': key_to_source[source_key],
                               'reference': pubmed_to_reference[pubmed_id],
                               'strain': None if strain_key is None or strain_key not in key_to_strain else key_to_strain[strain_key],
                               'experiment': key_to_experiment[experiment_format_name] if experiment_format_name in key_to_experiment else key_to_experiment[experiment_eco_id],
                               'locus1': key_to_bioentity[bioent1_key],
                               'locus2': key_to_bioentity[bioent2_key],
                               'direction': direction,
                               'pvalue': pvalue,
                               'fdr': fdr,
                               'construct': strain_background,
                               'properties': conditions}
                    else:
                        print 'Bioentity or strain or reference or source or experiment not found: ' + str(bioent1_key) + ' ' + \
                              str(bioent2_key) + ' ' + experiment_eco_id + ' ' + experiment_format_name + ' ' + str(strain_key) + ' ' + str(pubmed_id) + ' ' + str(source_key)

        nex_session.close()
    return regulation_evidence_starter



# --------------------- Convert Protein Sequence Evidence ---------------------
def make_protein_sequence_evidence_starter(nex_session_maker, strain_key, protein_sequence_filename, protparam_data):
    from src.sgd.model.nex.misc import Source, Strain
    from src.sgd.model.nex.bioentity import Locus
    def protein_sequence_evidence_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_bioentity = dict([(x.unique_key(), x) for x in nex_session.query(Locus).all()])
        key_to_strain = dict([(x.unique_key(), x) for x in nex_session.query(Strain).all()])

        f = open(protein_sequence_filename, 'r')
        for bioentity_name, residues in get_sequence_library_fsa(f).iteritems():
            bioentity_key = (bioentity_name, 'LOCUS')
            if bioentity_key[0] == 'tS(GCU)L':
                bioentity_key = ('tX(XXX)L', 'LOCUS')
            elif bioentity_key[0] == 'tT(XXX)Q2':
                bioentity_key = ('tT(UAG)Q2', 'LOCUS')

            if bioentity_key in key_to_bioentity:
                bioentity = key_to_bioentity[bioentity_key]

                basic_info = {'source': key_to_source['SGD'],
                           'strain': key_to_strain[strain_key],
                           'locus': bioentity,
                           'protein_type': 'PROTEIN',
                           'residues': residues}

                protparam_key = bioentity_name if strain_key == 'S288C' else bioentity_name + '_' + (strain_key if strain_key != 'CENPK' else 'CEN.PK2-1Ca')
                if protparam_key in protparam_data:
                    ppdata = protparam_data[protparam_key]
                    basic_info['molecular_weight'] = ppdata[1]
                    basic_info['pi'] = ppdata[2]
                    basic_info['gravy_score'] = ppdata[6]
                    basic_info['aromaticity_score'] = ppdata[7]
                    basic_info['cai'] = ppdata[8]
                    basic_info['codon_bias'] = ppdata[9]
                    basic_info['fop_score'] = ppdata[10]
                    try:
                        basic_info['carbon'] = int(ppdata[31])
                        basic_info['hydrogen'] = int(ppdata[32])
                        basic_info['nitrogen'] = int(ppdata[33])
                        basic_info['oxygen'] = int(ppdata[34])
                        basic_info['sulfur'] = int(ppdata[35])
                    except:
                        print 'Trouble with protparam: ' + str(ppdata)
                    basic_info['instability_index'] = ppdata[36]
                    basic_info['all_cys_ext_coeff'] = ppdata[37]
                    basic_info['no_cys_ext_coeff'] = ppdata[38]
                    basic_info['aliphatic_index'] = ppdata[39].strip()

                else:
                    print 'Protparam not found: ' + str(protparam_key)

                yield basic_info

        f.close()
        nex_session.close()
    return protein_sequence_evidence_starter

# --------------------- Convert Expression Evidence ---------------------
def make_expression_evidence_starter(nex_session_maker, expression_dir):
    from src.sgd.model.nex.misc import Source
    from src.sgd.model.nex.bioitem import Dataset, Datasetcolumn
    def expression_evidence_starter():
        nex_session = nex_session_maker()

        key_to_source = dict([(x.unique_key(), x) for x in nex_session.query(Source).all()])
        key_to_dataset = dict([(x.unique_key(), x) for x in nex_session.query(Dataset).all()])
        key_to_dataset_column = dict([(x.unique_key(), x) for x in nex_session.query(Datasetcolumn).all()])

        for path in os.listdir(expression_dir):
            if os.path.isdir(expression_dir + '/' + path):
                for file in os.listdir(expression_dir + '/' + path):
                    dataset_key = (file[:-4], 'DATASET')
                    if dataset_key in key_to_dataset:
                        f = open(expression_dir + '/' + path + '/' + file, 'r')
                        pieces = f.next().split('\t')
                        f.close()

                        for i in range(len(pieces)-3):
                            datasetcolumn_key = (file[:-4] + '.' + str(i), 'DATASETCOLUMN')
                            yield {
                                    'reference': key_to_dataset[dataset_key].reference,
                                    'source': key_to_source['SGD'],
                                    'datasetcolumn': None if datasetcolumn_key not in key_to_dataset_column else key_to_dataset_column[datasetcolumn_key]
                            }

        nex_session.close()
    return expression_evidence_starter

def get_alias_info(expression_file, key_to_locus, aliases):
    alias_used_count = 0
    undefined_alias_used_count = 0
    undefined_aliases = set()
    completely_undefined_count = 0
    completely_undefined = set()
    evidences = None
    for row in make_file_starter(expression_file)():
        if evidences is None:
            evidences = []
        elif row[0] != 'EWEIGHT':
            locus_key = row[0]
            if locus_key in aliases:
                alias_used_count += 1
                if len(aliases[locus_key]) > 1:
                    undefined_alias_used_count +=1
                    undefined_aliases.add(locus_key)
            elif locus_key not in key_to_locus:
                completely_undefined_count += 1
                completely_undefined.add(locus_key)
    print '\t'.join([expression_file, str(alias_used_count), str(undefined_alias_used_count), str(completely_undefined_count), str(undefined_aliases), str(completely_undefined)])

def make_expression_data_starter(nex_session_maker, expression_file, dataset_id, channel_count, key_to_locus, aliases):
    from src.sgd.model.nex.evidence import Expressionevidence
    from src.sgd.model.nex.bioitem import Datasetcolumn, Dataset
    def expression_evidence_starter():
        nex_session = nex_session_maker()
        print dataset_id
        dataset = nex_session.query(Dataset).filter_by(id=dataset_id).first()
        key_to_evidence = dict([(x.unique_key(), x) for x in nex_session.query(Expressionevidence).filter(Expressionevidence.datasetcolumn_id.in_([y.id for y in dataset.datasetcolumns])).all()])
        key_to_datasetcolumn = dict([(x.unique_key(), x) for x in nex_session.query(Datasetcolumn).all()])


        evidences = None
        locii_not_found = 0
        max_value = 0
        has_negative = False
        for row in make_file_starter(expression_file)():
            if evidences is None:
                evidences = []
                for file_order in range(0, len(row)-3):
                    datasetcolumn_key = (dataset.format_name + '.' + str(file_order), 'DATASETCOLUMN')
                    if datasetcolumn_key in key_to_datasetcolumn:
                        evidence_key = ('EXPRESSION', key_to_datasetcolumn[datasetcolumn_key].id)
                        if evidence_key in key_to_evidence:
                            evidences.append(key_to_evidence[evidence_key])
                        else:
                            print 'Evidence not found: ' + str(evidence_key)
                            evidences.append(None)
                    else:
                        print 'Datasetcolumn not found: ' + str(datasetcolumn_key)
            elif row[0] != 'EWEIGHT':
                locus_key = row[0]
                locus = None
                if locus_key in key_to_locus and (locus_key not in aliases or len(aliases[locus_key]) == 1):
                    locus = key_to_locus[locus_key]
                elif locus_key in aliases and len(aliases[locus_key]) == 1:
                    locus = list(aliases[locus_key])[0]
                if locus is not None:
                    log_sum = 0
                    n = 0
                    for value in row[3:]:
                        try:
                            dec_value = Decimal(value)
                            if dec_value < 0:
                                has_negative = True
                            elif dec_value > max_value:
                                max_value = dec_value
                            log_sum += 2**dec_value
                            n += 1
                        except:
                            pass
                    if log_sum != 0:
                        log_sum = math.log(log_sum, 2)
                        log_n = math.log(n, 2)
                        for i in range(0, len(evidences)):
                            if evidences[i] is not None:
                                try:
                                    yield {
                                        'locus_id': locus.id,
                                        'evidence_id': evidences[i].id,
                                        'value': Decimal(row[i+3]) if channel_count == 2 else Decimal(float(row[i+3]) + log_n - log_sum).quantize(Decimal('1.000'))
                                    }
                                except:
                                    pass
                                    #print 'Bad value: ' + str(row[i+3])
                else:
                    #print 'Locus not found: ' + str(locus_key)
                    locii_not_found += 1
        print 'Locii not found: ' + str(locii_not_found)
        print channel_count, has_negative, max_value

        nex_session.close()
    return expression_evidence_starter