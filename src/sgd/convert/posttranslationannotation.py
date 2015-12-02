from src.sgd.convert import basic_convert, remove_nones

__author__ = 'sweng66'

SRC = 'SGD'
TAXON_ID = "TAX:4932"

def posttranslationannotation_starter(bud_session_maker):
 
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.taxonomy import Taxonomy
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.psimod import Psimod

    nex_session = get_nex_session()

    pmid_to_reference_id = dict([(x.pmid, x.id) for x in nex_session.query(Reference).all()])
    term_to_psimod_id = dict([(x.display_name, x.id) for x in nex_session.query(Psimod).all()])

    name_to_dbentity_id = {}
    for x in nex_session.query(Locus).all():
        name_to_dbentity_id[x.systematic_name] = x.id
        if x.gene_name:
            name_to_dbentity_id[x.gene_name] = x.id

    taxid_to_taxonomy_id =  dict([(x.taxid, x.id) for x in nex_session.query(Taxonomy).all()])
    taxonomy_id = taxid_to_taxonomy_id.get(TAXON_ID)

    modification_to_psimod_term_mapping = get_psimod_mapping()
    
    file_names = ['src/sgd/convert/data/methylationSitesPMID25109467.txt',
                  'src/sgd/convert/data/ubiquitinationSites090314.txt',
                  'src/sgd/convert/data/phosphorylationUbiquitinationPMID23749301.txt',
                  'src/sgd/convert/data/succinylationAcetylation090914.txt',
                  'src/sgd/convert/data/gap1_Ub_PMID11500494.txt',
                  'src/sgd/convert/data/PTMsitesPMID25344756.txt',
                  'src/sgd/convert/data/PTMs_20150623.txt',
                  'src/sgd/convert/data/PTMsites062615.txt',
                  'src/sgd/convert/data/PTMsites091715.txt',
                  'src/sgd/convert/data/PTMsites102315.txt',
		  'src/sgd/convert/data/PTMsites112115.txt']
    
    for file_name in file_names:
        print "LOADING DATA from: ", file_name
        f = open(file_name, 'r')
        header = True
        for line in f:
            if header:
                header = False
            else:
                pieces = line.split('\t')
                dbentity_id = name_to_dbentity_id.get(pieces[0])
                if dbentity_id is None:
                    print "The ", pieces[0], " is not in the DBENTITY table."
                    continue
                site = pieces[1].strip()
                site_residue = site[0]
                site_index = int(site[1:])
                # site_functions = pieces[2]
                psimod_term = modification_to_psimod_term_mapping.get(pieces[3])
                if psimod_term is None:
                    print "The modification type ", pieces[3], " can not be mapped to a PSIMOD term."
                    continue
                psimod_id = term_to_psimod_id.get(psimod_term)
                if psimod_id is None:
                    print "The PSIMOD term ", psimod_term, " is not in PSIMOD table."
                    continue
                source = pieces[5]
                reference_id = pmid_to_reference_id.get(int(pieces[6].replace('PMID:', '')))
                if reference_id is None:
                    print "The PMID=", pieces[6].replace('PMID:', ''), " is not in REFERENCEDBENTITY table."
                    continue

                obj_json = { "source": { "display_name": source },
                             "dbentity_id": dbentity_id,
                             "reference_id": reference_id,
                             "psimod_id": psimod_id,
                             "taxonomy_id": taxonomy_id,
                             "site_index": site_index,
                             "site_residue": site_residue }
                             
                if pieces[4]:
                    for modifier in pieces[4].upper().split('|'):
                        modifier_id = name_to_dbentity_id.get(modifier)
                        if modifier is None:
                            print "The modifier: ", modifier, " is not in LOCUSDBENTITY table."
                            continue
                        obj_json['modifier_id'] = modifier_id
                        yield obj_json
                else:
                    yield obj_json

        f.close()


def get_psimod_mapping():

    return { "2-amino-3-oxo-butanoic acid": "2-amino-3-oxobutanoic acid",
             "acetylation": "acetylated residue",
             "butyrylation": "butanoylated residue", 
             "carbamidomethylation": "carbamoylated residue", 
             "deacetylation": "deacetylation residue",
             "deamidation": "deamidation residue", 
             "demethylation": "demethylation residue",
             "dimethylation": "dimethylated residue", 
             "ethylation": "ethylated residue", 
             "methylation": "methylated residue", 
             "monomethylation": "monomethylated residue",
             "monoubiquitination": "ubiquitinylated lysine", 
             "oxidation": "methionine oxidation with neutral loss of 64 Da",
             "palmitoylation": "palmitoylated residue", 
             "phosphorylation": "phosphorylated residue",
             "piperidination": "piperidination residue",
             "propionylation": "propanoylated residue", 
             "succinylation": "succinylated residue",
             "sumoylation": "sumoylated lysine", 
             "thiophosphorylation": "thiophosphorylated residue",
             "trimethylation": "trimethylated residue", 
             "ubiquitination": "ubiquitinylated lysine" }

def get_nex_session():

    from src.sgd.convert.util import prepare_schema_connection
    from src.sgd.convert import config
    from src.sgd.model import nex

    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)

    return nex_session_maker()

if __name__ == '__main__':
    from src.sgd.convert import config
    basic_convert(config.BUD_HOST, config.NEX_HOST, posttranslationannotation_starter, 'posttranslationannotation', lambda x: (x['dbentity_id'], x['reference_id'], x['psimod_id'], x['site_index'], x['site_residue'], x.get('modifier_id')))


