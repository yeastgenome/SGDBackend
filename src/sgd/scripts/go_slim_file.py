__author__ = 'kelley'

from sqlalchemy.orm import joinedload
from src.sgd.convert import prepare_schema_connection, config
from src.sgd.model import bud, nex, perf
from sqlalchemy import or_

def make_go_slim_file(nex_session_maker):
    from src.sgd.model.nex.evidence import Goevidence
    from src.sgd.model.nex.bioconcept import Bioconceptrelation
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.bioconcept import Bioconcept

    nex_session = nex_session_maker()

    id_to_bioconcept = dict([(x.id, x) for x in nex_session.query(Bioconcept).all()])
    id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])


    go_slim_terms = set([x.parent_id for x in nex_session.query(Bioconceptrelation).filter_by(relation_type='GO_SLIM').all()])
    root_terms = set([x.id for x in id_to_bioconcept.values() if x.format_name == 'molecular_function' or x.format_name == 'biological_process' or x.format_name == 'cellular_component'])
    bioconcept_id_to_parent_ids = dict([(x, []) for x in id_to_bioconcept.keys()])

    for relation in nex_session.query(Bioconceptrelation).filter(or_(Bioconceptrelation.relation_type == 'is a', Bioconceptrelation.relation_type == 'part of')).all():
        bioconcept_id_to_parent_ids[relation.child_id].append(relation.parent_id)

    entries = set()
    mapped_to_some_go_term = set()
    for evidence in nex_session.query(Goevidence).filter(Goevidence.annotation_type != 'computational'):
        bioentity_id = evidence.locus_id
        bioconcept_ids = [evidence.go_id]
        mapped_to_some_go_term.add(bioentity_id)
        while len(bioconcept_ids) > 0:
            new_bioconcept_ids = []
            for bioconcept_id in bioconcept_ids:
                if bioconcept_id in go_slim_terms and bioconcept_id not in root_terms:
                    entries.add((bioentity_id, bioconcept_id))
                new_bioconcept_ids.extend(bioconcept_id_to_parent_ids[bioconcept_id])
            bioconcept_ids = new_bioconcept_ids

        if evidence.go_id in root_terms:
            entries.add((bioentity_id, evidence.go_id))

    slim_file = open('go_slim_nex.txt', 'w+')
    for bioentity_id, bioconcept_id in entries:
        bioentity = id_to_bioentity[bioentity_id]
        bioconcept = id_to_bioconcept[bioconcept_id]
        if bioentity.qualifier != 'Dubious':
            slim_file.write('\t'.join([bioentity.display_name, bioentity.sgdid, bioconcept.display_name, bioconcept.go_id]) + '\n')
            if bioentity_id in mapped_to_some_go_term:
                mapped_to_some_go_term.remove(bioentity_id)

    for bioentity_id in mapped_to_some_go_term:
        bioentity = id_to_bioentity[bioentity_id]
        if bioentity.qualifier != 'Dubious':
            slim_file.write('\t'.join([bioentity.display_name, bioentity.sgdid, 'other', '']) + '\n')

    slim_file.close()
    nex_session.close()

def read_slim_file(filename, sgdid_column_index, goid_column_index):
    relationships = set()
    f = open(filename, 'r')
    for line in f:
        pieces = line.split('\t')
        relationships.add((pieces[sgdid_column_index].strip(), pieces[goid_column_index].strip()))
    f.close()
    return relationships

if __name__ == "__main__":
    #nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-master-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    #make_go_slim_file(nex_session_maker)

    nex = read_slim_file('go_slim_nex.txt', 1, 3)
    bud = read_slim_file('go_slim_mapping.tab.txt', 2, 5)

    print list(nex)[0:5]
    print list(bud)[0:5]

    print 'In both: ' + str(len(nex & bud))
    print 'Total in nex: ' + str(len(nex))
    print 'In nex only: ' + str(len(nex - bud))
    print 'Total in bud: ' + str(len(bud))
    print 'In bud only: ' + str(len(bud - nex))

    for entry in nex - bud:
        print entry

    #for entry in bud - nex:
    #    print entry