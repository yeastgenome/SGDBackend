from src.sgd.convert import basic_convert

__author__ = 'sweng66'

def phenotypeannotation_starter(bud_session_maker):
    from src.sgd.model.bud.phenotype import PhenotypeFeature
    from src.sgd.model.bud.reference import Reflink
    from src.sgd.model.nex.phenotype import Phenotype
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.apo import Apo
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.obi import Obi
    from src.sgd.model.nex.allele import Allele
    from src.sgd.model.nex.reporter import Reporter
    
    bud_session = bud_session_maker()
    nex_session = get_nex_session()

    bud_id_to_locus_id = dict([(x.bud_id, x.id) for x in nex_session.query(Locus).all()])
    phenotype_to_phenotype_id = dict([(x.display_name, x.id) for x in nex_session.query(Phenotype).all()])
    ref_bud_id_to_reference_id = dict([(x.bud_id, x.id) for x in nex_session.query(Reference).all()])
    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    allele_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Allele).all()])
    reporter_to_id = dict([(x.display_name, x.id) for x in nex_session.query(Reporter).all()])

    mutant_to_id = {}
    experiment_to_id = {}
    for nex_obj in nex_session.query(Apo).all():
        if nex_obj.apo_namespace == 'mutant_type':
            mutant_to_id[nex_obj.display_name] = nex_obj.id
        if nex_obj.apo_namespace == 'experiment_type':
            experiment_to_id[nex_obj.display_name] = nex_obj.id
            
    pheno_annot_bud_id_to_reference_id = {}
    for bud_obj in bud_session.query(Reflink).filter_by(tab_name='PHENO_ANNOTATION'):
        reference_id = ref_bud_id_to_reference_id.get(bud_obj.reference_id)
        if reference_id is not None:
            pheno_annot_bud_id_to_reference_id[bud_obj.primary_key] = reference_id

    for bud_obj in bud_session.query(PhenotypeFeature).all():

        ## locus
        locus_id = bud_id_to_locus_id.get(bud_obj.feature_id)
        if locus_id is None:
            print "The feature_no (bud_id) = ", bud_obj.feature_id, " is not found in Locusdbentity table." 
            continue

        ## phenotype = observable + qualifier
        phenotype = (bud_obj.observable + ('' if bud_obj.qualifier is None else ': ' + bud_obj.qualifier))[:500]
        phenotype_id = phenotype_to_phenotype_id.get(phenotype)
        if phenotype_id is None:
            print "The phenotype_no (bud_id) = ", bud_obj.phenotype_id, " is not found in Phenotype table." 
            continue

        ## experiment_type
        experiment_id = experiment_to_id.get(bud_obj.experiment_type)
        if experiment_id is None:
            print "The experiment_type = ", bud_obj.experiment_type, " is not found in Apo table."
            continue

        ## mutant_type
        mutant_id = mutant_to_id.get(bud_obj.mutant_type)
        if mutant_id is None:
            print "The mutant_type = ", bud_obj.mutant_type, " is not found in Apo table."
            continue

        ## reference - data from ref_link
        reference_id = pheno_annot_bud_id_to_reference_id.get(bud_obj.id)
        if reference_id is None:
            print "The reference for pheno_annotation_no = ", bud_obj.id, " is not in Reference table."
            continue

        ## taxonomy - data from expt_property => strain_background: S288C, W303, Other
        ## allele - data from expt_property
        ## reporter - data from expt_property

        strain_taxid_mapping = { "S288C":   'NCBITaxon:559292',
                                 "CEN.PK":  'NCBITaxon:889517',
                                 "FL100":   'NCBITaxon:947036',
                                 "RM11-1a": 'NCBITaxon:285006',
                                 "SK1":     'NCBITaxon:580239',
                                 "W303":    'NCBITaxon:580240',
                                 "Y55":     'NCBITaxon:580230',
                                 'Other':   'NCBITaxon:4932' }

        #  "D273-10B",  "JK9-3d", "SEY6210", "Sigma1278b", "X2180-1A"
        
        ## PROPERTY_TYPE                                                                                  
        # Chemical_pending                                                                                
        # chebi_ontology                                                                                  
        # Allele                                                                                          
        # Reporter                                                                                       
        # strain_background                                                                              
        # strain_name                                                                                    
        # Numerical_value                                                                                 
        # Condition                                                                                       
        # Details     

        taxonomy_id = ''
        allele_id = ''
        reporter_id = ''
        # print locus_id, phenotype_id, experiment_id, mutant_id, reference_id


        detail_data = []



        if bud_obj.experiment_properties is not None:
            for exptProp in bud_obj.experiment_properties:
                print "\t", exptProp.type, exptProp.value
                if exptProp.type == 'strain_background' and exptProp.value in strain_taxid_mapping:
                    taxid = strain_taxid_mapping[exptProp.value]
                    taxonomy_id = taxid_to_taxonomy_id.get(taxid)
                if exptProp.type == 'Allele':
                    allele_id = allele_to_id.get(exptProp.value)
                    if allele_id is None:
                        print "\t\tAllele: ", exptProp.value, " is not in Allele table."
                if exptProp.type == 'Reporter':
                    reporter_id =reporter_to_id.get(exptProp.value)
                    if reporter_id is None:
                        print "\t\tReporter: ", exptProp.value, " is not in Reporter table."
                if exptProp.type in ['Chemical_pending', 'chebi_ontology', 'strain_name', 'Numerical_value', 'Condition', 'Details']:
                    detail_data.append({ 'detail_type': ?,
                                         'detail_name': ?,
                                         'detail_value':?,
                                         'date_created': str(exptProp.date_created), 
                                         'created_by': exptProp.created_by })

        obj_json = {
            'source': {'display_name': 'SGD'},
            'locus_id': locus_id,
            'phenotype_id': phenotype_id,
            'experiment_id': experiment_id,
            'mutant_id': mutant_id,
            'reference_id': reference_id,
            'bud_id': bud_obj.id,
            'date_created': str(bud_obj.date_created),
            'created_by': bud_obj.created_by
        }
        if taxonomy_id is not None:
            obj_json['taxonomy_id'] = taxonomy_id
        if allele_id is not None:
            obj_json['allele_id'] = allele_id
        if reporter_id is not None:
            obj_json['reporter_id'] = reporter_id
        if len(detail_data) > 0:
            obj_json['detail_data'] = detail_data

        yield obj_json

    bud_session.close()


def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()


if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, phenotypeannotation_starter, 'phenotypeannotation', lambda x: (x['locus_id'], x['phenotype_id'], x['mutant_id'], x['experiment_id'], x['reference_id']))


