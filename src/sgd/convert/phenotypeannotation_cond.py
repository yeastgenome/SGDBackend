from src.sgd.convert import basic_convert

__author__ = 'sweng66'

TAXON = "TAX:559292"

def phenotypeannotation_cond_starter(bud_session_maker):
    from src.sgd.model.nex.phenotypeannotation import Phenotypeannotation
    from src.sgd.model.bud.phenotype import PhenotypeFeature, ExperimentProperty, Experiment_ExperimentProp
    nex_session = get_nex_session()
    bud_session = bud_session_maker()
    expt_property_id_to_exptprop_obj= dict([(x.id, x) for x in bud_session.query(ExperimentProperty).all()])
    expt_property_id_to_expt_id = dict([(x.experiment_property_id, x.experiment_id) for x in bud_session.query(Experiment_ExperimentProp).all()])

    expt_id_to_bud_annotation_no_list = {}
    for x in bud_session.query(PhenotypeFeature).all():
        annotation_no_list = []
        if x.experiment_id in expt_id_to_bud_annotation_no_list:
            annotation_no_list = expt_id_to_bud_annotation_no_list[x.experiment_id]
        annotation_no_list.append(x.id)
        expt_id_to_bud_annotation_no_list[x.experiment_id] = annotation_no_list

    bud_annotation_no_to_annotation_id = dict([(x.bud_id, x.id) for x in nex_session.query(Phenotypeannotation).all()])

    ## load "chebi_ontology" & "Chemical_pending" 
    
    for x in bud_session.query(ExperimentProperty).all():
        
        if x.type in ['chebi_ontology', 'Chemical_pending']:
            condition_class = 'chemical'
            condition_name = x.value
            condition_value = x.description
            if condition_value is None:
                condition_value = ''

            expt_id = expt_property_id_to_expt_id.get(x.id)
            bud_annotation_no_list = expt_id_to_bud_annotation_no_list.get(expt_id)
            if bud_annotation_no_list is None:
                print "The experiment_no: ", expt_id, " is not in the BUD.pheno_annotation table"
                continue
            for bud_annotation_no in bud_annotation_no_list:
                annotation_id = bud_annotation_no_to_annotation_id.get(bud_annotation_no)
                if annotation_id is None:
                    print "The bud_id: ", bud_annotation_no, " is not in the PHENOTYPEANNOTATION table."
                    continue

                yield { 'annotation_id': annotation_id,
                        'condition_class': condition_class,
                        'condition_name': condition_name,
                        'condition_value': condition_value,
                        'date_created': str(x.date_created),
                        'created_by': x.created_by }

    ## load Condition  
    f = open("src/sgd/convert/data/phenotypeConditions032516.txt")
    for line in f:

        pieces = line.strip().split("\t")
        if pieces[0].startswith('EXPT'):
            continue
        if len(pieces) < 5:
            print "bad row: ", line 
            continue
        expt_id = expt_property_id_to_expt_id.get(int(pieces[0]))
        if expt_id is None:
            print "The expt_property_no: ", pieces[0], " is not in the BUD.expt_property table."
            continue
        bud_annotation_no_list = expt_id_to_bud_annotation_no_list.get(expt_id)
        if bud_annotation_no_list is None:
            print "The experiment_no: ", expt_id, " is not in the BUD.pheno_annotation table"
            continue
        for bud_annotation_no in bud_annotation_no_list:
            annotation_id = bud_annotation_no_to_annotation_id.get(bud_annotation_no)
            if annotation_id is None:
                print "The bud_id: ", bud_annotation_no, " is not in the PHENOTYPEANNOTATION table."
                continue
        
            value = ''
            if pieces[3] != '(null)':
                value = pieces[3].replace('"', '')

            exptprop_obj = expt_property_id_to_exptprop_obj.get(int(pieces[0]))
            if exptprop_obj is None:
                print "The expt_property_no:", pieces[0], " is not in the BUD.expt_property table."
                continue

            yield { 'annotation_id': annotation_id,
                    'condition_class': pieces[4],
                    'condition_name': pieces[2].replace('"', ''),
                    'condition_value': value,
                    'date_created': str(exptprop_obj.date_created),
                    'created_by': exptprop_obj.created_by }
    
    f.close()
    nex_session.close()    

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, phenotypeannotation_cond_starter, 'phenotypeannotation_cond', lambda x: (x['annotation_id'], x['condition_class'], x['condition_name'], x.get('condition_value')))
 
