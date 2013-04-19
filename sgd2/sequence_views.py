'''
Created on Mar 23, 2013

@author: kpaskov
'''
from pyramid.response import Response
from pyramid.view import view_config
from query import get_bioent, get_sequences

@view_config(route_name='sequence', renderer='json')
def sequence(request):
    if 'bioent_name' in request.GET:
        bioent_name = request.GET['bioent_name']

        bioent = get_bioent(bioent_name)
        if bioent is None:
            return Response(status_int=500, body='Bioent could not be found.')
        
        seqs, id_to_type = get_sequences(bioent)
        
        dna_seqs = [seq for seq in seqs if id_to_type[seq.bioent_id]=='GENE']
        return {'GENE': dict([(seq.strain.name, (formatted_residues(seq), formatted_tags(seq), seq.strand, seq.min_coord, seq.max_coord)) for seq in seqs if id_to_type[seq.bioent_id]=='GENE']),
            'TRANSCRIPT': dict([(seq.strain.name, (formatted_residues(seq), formatted_tags(seq), seq.strand, seq.min_coord, seq.max_coord)) for seq in seqs if id_to_type[seq.bioent_id]=='TRANSCRIPT']),
            'PROTEIN': dict([(seq.strain.name, (formatted_residues(seq), formatted_tags(seq), seq.strand, seq.min_coord, seq.max_coord)) for seq in seqs if id_to_type[seq.bioent_id]=='PROTEIN']),
            'DNA_VAR': variation_map(dna_seqs)}

    else:
        return Response(status_int=500, body='No Bioent or Strain specified.')
    
def formatted_residues(seq):
    if seq.seq_type == 'DNA':
        return  ' '.join(seq.residues[i:i+3] for i in range(0, len(seq.residues), 3)) + ' '
    else:
        return seq.residues
        
def formatted_tags(seq):
    colors = {'intron': 'green', 'CDS': 'red', 'X_region': 'blue', 'Y_region':'purple', 'Z1_region':'yellow', 'Z2_region':'orange'}
    tags = []  
    for tag in seq.seq_tags:
        if (tag.seqtag_type != 'ORF' and tag.length < seq.length) or len(seq.seq_tags) == 1:
            start = 100.0*tag.relative_coord/seq.length
            length = 100.0*tag.length/seq.length
            color = 'black'
            if tag.seqtag_type in colors:
                color = colors[tag.seqtag_type]
            tags.append([tag.seqtag_type, start, length, color])
    return tags

def variation_map(seqs):
    max_length = max([seq.length for seq in seqs])
    red_count = []
    for i in range(0, max_length):
        freqs = {'G':0, 'C':0, 'A':0, 'T':0, 'R':0, 'Y':0, 'S':0, 'W':0, 'M':0, 'K':0, 'V':0, 'B':0, 'H':0, 'D':0, 'N':0, 'X':0, 'U':0, 'Missing':0}
        get_frequences(i, seqs, freqs)
        red_count.append(calc_red_count(freqs))
        
    current_value = red_count[0]
    starting_point = 0
    tags = []
    for i in range(0, max_length):
        if current_value != red_count[i]:
            start = 100.0*(starting_point-1)/max_length
            length = 100.0*(i-starting_point)/max_length
            if red_count[i-1] > 0:
                tags.append([str(red_count[i-1]), start, length, 'red'])
            
            current_value = red_count[i]
            starting_point = i
    return tags
        
        
def get_frequences(i, seqs, freqs):
    for seq in seqs:
        if i < seq.length:
            r = seq.residues[i]
        else:
            r = 'Missing'
        freqs[r] = freqs[r]+1
    
def calc_red_count(freqs):
    total = sum(freqs.values())
    max_value = max(freqs.values())
    return total-max_value
    