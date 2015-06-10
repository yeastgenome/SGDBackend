genetic_type_to_phenotype = {'Dosage Lethality'               : 'inviable',
                             'Dosage Rescue'                  : 'wildtype',
                             'Dosage Growth Defect'           : 'slow growth',
                             'Epistatic MiniArray Profile'    : 'Not available',
                             'Negative Genetic'               : 'Not available',
                             'Positive Genetic'               : 'Not available',
                             'Phenotypic Enhancement'         : 'Not available',
                             'Phenotypic Suppression'         : 'Not available',
                             'Synthetic Growth Defect'        : 'slow growth',
                             'Synthetic Haploinsufficiency'   : 'Not available',
                             'Synthetic Lethality'            : 'inviable',
                             'Synthetic Rescue'               : 'wildtype'
}

old_phenotype_to_new_phenotype = {'inviable'    : {'experiment_type' : 'classical genetics',
                                                   'mutant_type'     : 'unspecified',
                                                   'observable'      : 'inviable'},
                                 'slow growth'  : {'experiment_type' : 'classical genetics',
                                                   'mutant_type'     : 'unspecified',
                                                   'qualifier'       : 'decreased',
                                                   'observable'      : 'vegetative growth'},
                                 'wildtype'     : {'experiment_type' : 'classical genetics',
                                                   'mutant_type'     : 'unspecified',
                                                   'qualifier'       : 'normal',
                                                   'observable'      : 'vegetative growth'}
}

email_receiver = ['sweng@stanford.edu']
email_subject = 'BioGrid loading summary'

