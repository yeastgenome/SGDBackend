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
            'PROTEIN': dict([(seq.strain.name, (formatted_residues(seq), formatted_tags(seq), seq.strand, seq.min_coord, seq.max_coord)) for seq in seqs if id_to_type[seq.bioent_id]=='PROTEIN'])}

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
    print 'working'