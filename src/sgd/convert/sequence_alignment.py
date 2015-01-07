__author__ = 'kpaskov'

# Run clustal omega
# http://www.clustal.org/omega/
# for file in *.txt; do echo "$file"; ./clustalo -i $file > /Users/kpaskov/Projects/SGDBackend/src/sgd/convert/alignments/$file; done;
def get_sequences(nex_session_maker):
    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.evidence import Strain
    from src.sgd.model.nex.evidence import DNAsequenceevidence, Proteinsequenceevidence

    nex_session = nex_session_maker()
    id_to_bioentity = dict([(x.id, x) for x in nex_session.query(Bioentity).all()])
    id_to_strain = dict([(x.id, x) for x in nex_session.query(Strain).all()])

    for i, bioentity in enumerate(id_to_bioentity.values()):
        dnasequenceevidences = nex_session.query(DNAsequenceevidence).filter_by(dna_type='GENOMIC').filter_by(locus_id=bioentity.id).all()
        f = open('src/sgd/convert/strain_sequences/' + str(bioentity.id) + '.txt', 'w+')
        f.write('\n'.join(['>' + id_to_strain[dnasequenceevidence.strain_id].display_name + '\n' + dnasequenceevidence.residues for dnasequenceevidence in dnasequenceevidences]))
        f.close()

        if i%100 == 0:
            print i

    nex_session.close()

# def load_alignments():


# def hierarchical_clustering():
#     a = np.array([[0.1,   2.5],
#               [1.5,   .4 ],
#               [0.3,   1  ],
#               [1  ,   .8 ],
#               [0.5,   0  ],
#               [0  ,   0.5],
#               [0.5,   0.5],
#               [2.7,   2  ],
#               [2.2,   3.1],
#               [3  ,   2  ],
#               [3.2,   1.3]])
#
#     z = linkage(a)
#     print to_tree(z)


if __name__ == '__main__':
    from src.sgd.model import nex
    from src.sgd.convert import prepare_schema_connection, config
    nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, 'sgd-dev-db.stanford.edu:1521', config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
    get_sequences(nex_session_maker)

    # import numpy as np
    # from fastcluster import to_tree, linkage
    # hierarchical_clustering()

    # load_alignments()


