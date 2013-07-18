'''
Created on Jul 12, 2013

@author: kpaskov
'''
from go_enrichment.hypergeom import FishersExactTest
from query import session
import datetime

biocon_id_to_bioent_ids = {}
biocon_id_to_link = {}

def setup_go_enrichment_analysis():
    from model_new_schema.go import Gofact, Go

    biofacts = session.query(Gofact).all()
    
    for biofact in biofacts:
        bioent_id = biofact.bioent_id
        biocon_id = biofact.biocon_id
        
        if biocon_id in biocon_id_to_bioent_ids:
            biocon_id_to_bioent_ids[biocon_id].add(bioent_id)
        else:
            biocon_id_to_bioent_ids[biocon_id] = set([bioent_id])  
            
    biocons = session.query(Go).all() 
    for biocon in biocons:
        biocon_id_to_link[biocon.id] = biocon.name_with_link

cached_p_values = {}

def calc_p_value(overlap, go_length, gene_list_size, genome_size):
    cache_key = (overlap, go_length, gene_list_size)
    if cache_key in cached_p_values:
        return cached_p_values[cache_key]
    else:
        a = overlap
        b = gene_list_size-overlap
        c = go_length-overlap
        d = genome_size-go_length-b
        ft = FishersExactTest([[a, b], [c, d]])
        p_value = ft.two_tail_p()
        cached_p_values[cache_key] = p_value
        return p_value

def filter_by_p_value_cutoff(p_value_cutoff, tuples_being_considered, gene_list_size, genome_size):
    max_overlap = max([overlap for biocon_id, overlap, go_length in tuples_being_considered])
    max_go_length = max([go_length for biocon_id, overlap, go_length in tuples_being_considered])
    overlap_to_max_go_length = [max_go_length] * (max_overlap+1)
    go_length_to_min_overlap = [1] * (max_go_length+1)
    
    final_tuples = []
    for biocon_id, overlap, go_length in tuples_being_considered:
        if overlap >= go_length_to_min_overlap[go_length] and go_length <= overlap_to_max_go_length[overlap]:
            p_value = calc_p_value(overlap, go_length, gene_list_size, genome_size)
            if p_value < p_value_cutoff:
                final_tuples.append([biocon_id_to_link[biocon_id], overlap, go_length, gene_list_size, genome_size, p_value])
            else:
                #Any tuple with this overlap or less must have at most this go_length
                for i in range(0, overlap+1):
                    overlap_to_max_go_length[i] = min(overlap_to_max_go_length[i], go_length)
                #Any tuple with this go_length or more must have at least this overlap
                for i in range(go_length, len(go_length_to_min_overlap)):
                    go_length_to_min_overlap[i] = max(go_length_to_min_overlap[i], overlap)
    return final_tuples  

def filter_by_num_results_cutoff(num_results, tuples_being_considered, gene_list_size, genome_size):
    max_overlap = max([overlap for biocon_id, overlap, go_length, ranking in tuples_being_considered])
    max_go_length = max([go_length for biocon_id, overlap, go_length, ranking in tuples_being_considered])
    overlap_to_max_go_length = [max_go_length] * (max_overlap+1)
    go_length_to_min_overlap = [1] * (max_go_length+1)
    top_ten_p_values = [1] * num_results
    max_of_top_ten_p_values = 1
    
    p_value_to_tuple = {}
    
#    final_tuples = []
#
    for biocon_id, overlap, go_length, ranking in tuples_being_considered:
#        p_value = calc_p_value(overlap, go_length, gene_list_size, genome_size)
#        final_tuples.append([biocon_id_to_link[biocon_id], overlap, go_length, gene_list_size, genome_size, p_value])
#  
        
        if overlap >= go_length_to_min_overlap[go_length] and go_length <= overlap_to_max_go_length[overlap]:
            p_value = calc_p_value(overlap, go_length, gene_list_size, genome_size)
            if p_value < .01 and p_value < max_of_top_ten_p_values:
                to_be_removed = max_of_top_ten_p_values
                top_ten_p_values.remove(to_be_removed)
                top_ten_p_values.append(p_value)
                max_of_top_ten_p_values = max(top_ten_p_values)
                
                p_value_to_tuple[p_value] = [biocon_id_to_link[biocon_id], overlap, go_length, gene_list_size, genome_size, p_value]
            
                if to_be_removed < 1:
                    biocon_link, overlap, go_length, gene_list_size, genome_size, p_value = p_value_to_tuple[to_be_removed]
                    #Any tuple with this overlap or less must have at most this go_length
                    for i in range(0, overlap+1):
                        overlap_to_max_go_length[i] = min(overlap_to_max_go_length[i], go_length)
                        #Any tuple with this go_length or more must have at least this overlap
                    for i in range(go_length, len(go_length_to_min_overlap)):
                        go_length_to_min_overlap[i] = max(go_length_to_min_overlap[i], overlap)
            else:
                #Any tuple with this overlap or less must have at most this go_length
                for i in range(0, overlap+1):
                    overlap_to_max_go_length[i] = min(overlap_to_max_go_length[i], go_length)
                #Any tuple with this go_length or more must have at least this overlap
                for i in range(go_length, len(go_length_to_min_overlap)):
                    go_length_to_min_overlap[i] = max(go_length_to_min_overlap[i], overlap)
                    
    print top_ten_p_values
    final_tuples = [p_value_to_tuple[x] for x in top_ten_p_values]
    return final_tuples  

def go_enrichment(my_bioent_ids):
    genome_size = 6234
    my_bioent_ids_set = set(my_bioent_ids)
    gene_list_size = len(my_bioent_ids_set)
    
    tuples_being_considered = []
    for biocon_id, bioent_ids in biocon_id_to_bioent_ids.iteritems():
        go_length = len(bioent_ids)
        if go_length > 5:
            overlap = len(my_bioent_ids_set & bioent_ids)
            pop_perc = 1.0*go_length/genome_size
            sample_perc = 1.0*overlap/gene_list_size
            if overlap > 0 and sample_perc > pop_perc:
                tuples_being_considered.append((biocon_id, overlap, go_length))

    #tuples_being_considered.sort(key=lambda (biocon_id, overlap, go_length, ranking): ranking, reverse=True)
    print len(tuples_being_considered)        
    final_tuples = filter_by_p_value_cutoff(.01, tuples_being_considered, gene_list_size, genome_size)
    #final_tuples = filter_by_num_results_cutoff(10, tuples_being_considered, gene_list_size, genome_size)

    
    return final_tuples
            
if __name__ == "__main__":
    start_time = datetime.datetime.now()
    setup_go_enrichment_analysis()
    print 'Setup time: ' + str(datetime.datetime.now() - start_time)
    start_time = datetime.datetime.now()
    go_enrichment([6668, 4334, 6505, 6884, 6541, 4770, 5152, 5736, 5258, 5586, 
                   4855, 4866, 5123, 5001, 6933, 5470, 6871, 6487, 6469, 5385, 
                   5455, 4275, 6778, 4662, 5471, 7050, 6404, 5079, 6674, 7003])
    print 'Enrichment time: ' + str(datetime.datetime.now() - start_time)
