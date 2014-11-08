__author__ = 'kpaskov'
from src.sgd.backend.nex import DBSession
import json

def get_snapshot():
    #Go
        from src.sgd.model.nex.bioconcept import Go, Bioconceptrelation
        from src.sgd.model.nex.evidence import Goevidence
        go_slim_ids = set([x.parent_id for x in DBSession.query(Bioconceptrelation).filter_by(relation_type='GO_SLIM').all()])
        go_terms = DBSession.query(Go).filter(Go.id.in_(go_slim_ids)).all()
        go_slim_terms = []
        go_relationships = [['Child', 'Parent']]
        for go_term in go_terms:
            obj_json = go_term.to_min_json()
            obj_json['descendant_annotation_gene_count'] = go_term.descendant_locus_count
            obj_json['direct_annotation_gene_count'] = go_term.locus_count
            obj_json['is_root'] = go_term.is_root
            go_slim_terms.append(obj_json)

            parents = [x.parent for x in go_term.parents if x.relation_type == 'is a']
            while parents is not None and len(parents) > 0:
                new_parents = []
                for parent in parents:
                    if parent.id in go_slim_ids:
                        go_relationships.append([go_term.id, parent.id])
                        break
                    else:
                        new_parents.extend([x.parent for x in parent.parents if x.relation_type == 'is a'])
                parents = new_parents

        #Phenotype
        from src.sgd.model.nex.bioconcept import Observable, Bioconceptrelation
        from src.sgd.model.nex.evidence import Phenotypeevidence
        phenotype_slim_ids = set([x.parent_id for x in DBSession.query(Bioconceptrelation).filter_by(relation_type='PHENOTYPE_SLIM').all()])
        phenotypes = DBSession.query(Observable).filter(Observable.id.in_(phenotype_slim_ids)).all()
        phenotype_slim_terms = []
        phenotype_relationships = [['Child', 'Parent']]
        for phenotype in phenotypes:
            obj_json = phenotype.to_min_json()
            obj_json['descendant_annotation_gene_count'] = phenotype.descendant_locus_count
            obj_json['direct_annotation_gene_count'] = phenotype.locus_count
            obj_json['is_root'] = phenotype.is_root
            phenotype_slim_terms.append(obj_json)

            parents = [x.parent for x in phenotype.parents if x.relation_type == 'is a']
            while parents is not None and len(parents) > 0:
                new_parents = []
                for parent in parents:
                    if parent.id in phenotype_slim_ids:
                        phenotype_relationships.append([phenotype.id, parent.id])
                        break
                    else:
                        new_parents.extend([x.parent for x in parent.parents if x.relation_type == 'is a'])
                parents = new_parents

        #Sequence
        from src.sgd.model.nex.bioentity import Locus
        from src.sgd.model.nex.bioitem import Contig
        from src.sgd.model.nex.evidence import DNAsequenceevidence
        from src.sgd.model.nex.misc import Strain

        id_to_strain = dict([(x.id, x) for x in DBSession.query(Strain)])
        contigs = DBSession.query(Contig).filter(Contig.strain_id == 1).all()
        labels = ['ORF', 'long_terminal_repeat', 'ARS', 'tRNA', 'transposable_element_gene', 'snoRNA', 'retrotransposon',
                  'telomere', 'rRNA', 'pseudogene', 'ncRNA', 'centromere', 'snRNA', 'multigene locus', 'gene_cassette',
                  'mating_locus', 'Verified', 'Dubious', 'Uncharacterized']

        contig_id_to_index = {}
        label_to_index = {}
        for contig in contigs:
            contig_id_to_index[contig.id] = len(contig_id_to_index)
        for label in labels:
            label_to_index[label] = len(label_to_index)

        locuses = DBSession.query(Locus).filter_by(bioent_status='Active').all()
        locus_id_to_label_index = dict([(x.id, label_to_index[x.locus_type]) for x in locuses if x.locus_type in label_to_index])
        locus_id_to_char_label_index = dict([(x.id, label_to_index[x.qualifier]) for x in locuses if x.qualifier is not None])

        data = [([0]*len(contigs)) for _ in range(len(labels))]

        print 'ready', len(labels), len(contigs), len(data), len(data[0])

        for evidence in DBSession.query(DNAsequenceevidence).filter_by(dna_type='GENOMIC').filter(DNAsequenceevidence.contig_id.in_(contig_id_to_index.keys())).all():
            locus_id = evidence.locus_id
            label_index = None if evidence.locus_id not in locus_id_to_label_index else locus_id_to_label_index[locus_id]
            contig_index = None if evidence.contig_id not in contig_id_to_index else contig_id_to_index[evidence.contig_id]
            if label_index is not None and contig_index is not None:
                data[label_index][contig_index] += 1

            if locus_id in locus_id_to_char_label_index and contig_index is not None:
                char_label_index = locus_id_to_char_label_index[locus_id]
                if char_label_index is not None:
                    data[char_label_index][contig_index] += 1

        columns = []
        for x in contigs:
            obj_json = x.to_min_json()
            obj_json['strain'] = id_to_strain[x.strain_id].to_min_json()
            obj_json['length'] = len(x.residues)
            columns.append(obj_json)

        return json.dumps({'phenotype_slim_terms': phenotype_slim_terms, 'phenotype_slim_relationships': phenotype_relationships,
                           'go_slim_terms': go_slim_terms, 'go_slim_relationships': go_relationships,
                           'data': data, 'columns': columns, 'rows': labels})