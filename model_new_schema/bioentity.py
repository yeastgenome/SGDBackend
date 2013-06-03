'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base, EqualityByIDMixin
from model_new_schema.evidence import Evidence
from model_new_schema.link_maker import add_link, bioent_link, bioent_wiki_link
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, Float
import datetime

class Bioentity(Base, EqualityByIDMixin):
    __tablename__ = 'bioent'
    
    id = Column('bioent_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    bioent_type = Column('bioent_type', String)
    dbxref_id = Column('dbxref', String)
    source = Column('source', String)
    status = Column('status', String)
    
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': bioent_type,
                       'polymorphic_identity':"BIOENTITY"}
    
    #Relationships
    bioconcepts = association_proxy('biofacts', 'bioconcept')
    aliases = relationship("Alias")
    alias_names = association_proxy('aliases', 'name')
    seq_ids = association_proxy('sequences', 'id')
    type = "BIOENTITY"
            
    def __init__(self, bioent_id, display_name, format_name, bioent_type, dbxref, source, status,
                 date_created, created_by):
        self.id = bioent_id
        self.display_name = display_name
        self.format_name = format_name
        self.bioent_type = bioent_type
        self.dbxref_id = dbxref
        self.source = source
        self.status = status
        self.date_created = date_created
        self.created_by = created_by
            
    def unique_key(self):
        return (self.format_name, self.bioent_type)
    
    #Database hybrid properties
    @hybrid_property
    def biorelations(self):
        return set(self.biorel_source + self.biorel_sink)
    @hybrid_property
    def alias_str(self):
        return ', '.join(self.alias_names)
    
    #Names and links     
    @hybrid_property
    def full_name(self, include_link=True):
        return self.display_name + ' (' + self.format_name + ')'
    @hybrid_property
    def link(self):
        return bioent_link(self)
    @hybrid_property
    def name_with_link(self):
        return add_link(self.display_name, self.link) 
    @hybrid_property
    def full_name_with_link(self):
        return add_link(self.full_name, self.link) 
    @hybrid_property
    def wiki_name_with_link(self):
        return add_link(self.wiki_link, self.wiki_link)
    @hybrid_property
    def wiki_link(self):
        return bioent_wiki_link(self)    
    
class BioentRelation(Base, EqualityByIDMixin):
    __tablename__ = "bioentrel"
    
    id = Column('biorel_id', Integer, primary_key = True)
    format_name = Column('format_name', String)
    display_name = Column('display_name', String)
    description = Column('description', String)
    biorel_type = Column('biorel_type', String)
    source_bioent_id = Column('bioent_id1', Integer, ForeignKey(Bioentity.id))
    sink_bioent_id = Column('bioent_id2', Integer, ForeignKey(Bioentity.id))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    type = 'BIORELATION'
    
    __mapper_args__ = {'polymorphic_on': biorel_type,
                       'polymorphic_identity':"BIORELATION"}
    
    #Relationships
    source_bioent = relationship('Bioentity', uselist=False, primaryjoin="BioentRelation.source_bioent_id==Bioentity.id", backref='biorel_source')
    sink_bioent = relationship('Bioentity', uselist=False, primaryjoin="BioentRelation.sink_bioent_id==Bioentity.id", backref='biorel_sink')
        
    def get_opposite(self, bioent):
        if bioent == self.source_bioent:
            return self.sink_bioent
        elif bioent == self.sink_bioent:
            return self.source_bioent
        else:
            return None
    
    def __init__(self, biorel_type, source_bioent_id, sink_bioent_id, session=None, biorel_id=None, created_by=None, date_created=None):
        self.source_bioent_id = source_bioent_id
        self.sink_bioent_id = sink_bioent_id
        self.biorel_type = biorel_type
        
        if session is None:
            self.created_by = created_by
            self.date_created = date_created
            self.id = biorel_id
        else:
            self.created_by = session.user
            self.date_created = datetime.datetime.now() 

class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'
    
    id = Column('alias_id', Integer, primary_key=True)
    bioent_id = Column('bioent_id', Integer, ForeignKey(Bioentity.id))
    name = Column('name', String)
    alias_type = Column('alias_type', String)
    used_for_search = Column('used_for_search', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
        
    def __init__(self, name, alias_type, used_for_search, session=None, alias_id=None, bioent_id=None, date_created=None, created_by=None):
        self.name = name
        self.alias_type = alias_type
        self.used_for_search = used_for_search
        
        if session is None:
            self.id = alias_id
            self.bioent_id = bioent_id
            self.date_created = date_created
            self.created_by = created_by
        else:
            self.date_created = datetime.datetime.now()
            self.created_by = session.user             
                       
class Gene(Bioentity):
    __tablename__ = "gene"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    qualifier = Column('qualifier', String)
    attribute = Column('attribute', String)
    name_description = Column('short_description', String)
    headline = Column('headline', String)
    description = Column('description', String)
    genetic_position = Column('genetic_position', String)
    gene_type = Column('gene_type', String)
    type = "GENE"
    
    transcript_ids = association_proxy('transcripts', 'id')
    
    __mapper_args__ = {'polymorphic_identity': 'GENE',
                       'inherit_condition': id == Bioentity.id}
    
    @hybrid_property
    def search_entry_title(self):
        return self.full_name_with_link
    @hybrid_property
    def search_description(self):
        return self.description
    @hybrid_property
    def search_additional(self):
        if len(self.aliases) > 0:
            return 'Aliases: ' + self.alias_str
        return None
    @hybrid_property
    def search_entry_type(self):
        return 'Gene'

    def __init__(self, bioent_id, display_name, format_name, dbxref, source, status,
                 gene_type, qualifier, attribute, short_description, headline, description, genetic_position,
                 date_created, created_by):
        Bioentity.__init__(self, bioent_id, display_name, format_name, 'GENE', dbxref, source, status, date_created, created_by)
        self.gene_type = gene_type
        self.qualifier = qualifier
        self.attribute = attribute
        self.short_description = short_description
        self.headline = headline
        self.description = description
        self.genetic_position = genetic_position
        
class Protein(Bioentity):
    __tablename__ = "protein"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    transcript_id = Column('transcript_id', Integer)
    
    molecular_weight = Column('molecular_weight', Integer)
    pi = Column('pi', Float)
    cai = Column('cai', Float)
    length = Column('length', Integer)
    n_term_seq = ('n_term_seq', String)
    c_term_seq = ('c_term_seq', String)
    codon_bias = ('codon_bias', Float)
    fop_score = Column('fop_score', Float)
    gravy_score = Column('gravy_score', Float)
    aromaticity_score = Column('aromaticity_score', Float)
    type = "PROTEIN"
    
    ala = Column('ala', Integer)
    arg = Column('arg', Integer)
    asn = Column('asn', Integer)
    asp = Column('asp', Integer)
    cys = Column('cys', Integer)
    gln = Column('gln', Integer)
    glu = Column('glu', Integer)
    gly = Column('gly', Integer)
    his = Column('his', Integer)
    ile = Column('ile', Integer)
    leu = Column('leu', Integer)
    lys = Column('lys', Integer)
    met = Column('met', Integer)
    phe = Column('phe', Integer)
    pro = Column('pro', Integer)
    thr = Column('thr', Integer)
    ser = Column('ser', Integer)
    trp = Column('trp', Integer)
    tyr = Column('tyr', Integer)
    val = Column('val', Integer)
    
    aliphatic_index = Column('aliphatic_index', Float)
    atomic_comp_H = Column('atomic_comp_h', Integer)
    atomic_comp_S = Column('atomic_comp_s', Integer)
    atomic_comp_N = Column('atomic_comp_n', Integer)
    atomic_comp_O = Column('atomic_comp_o', Integer)
    atomic_comp_C = Column('atomic_comp_c', Integer)
    half_life_yeast_in_vivo = Column('half_life_yeast_in_vivo', String)
    half_life_ecoli_in_vivo = Column('half_life_ecoli_in_vivo', String)
    half_life_mammalian_reticulocytes_in_vitro = Column('half_life_mammalian', String)
    extinction_coeff_no_cys_residues_as_half_cystines = Column('extinction_coeff_no_half', Integer)
    extinction_coeff_all_cys_residues_reduced = Column('extinction_coeff_all_reduced', Integer)
    extinction_coeff_all_cys_residues_as_half_cystines = Column('extinction_coeff_all_half', Integer)
    extinction_coeff_all_cys_pairs_form_cystines = Column('extinction_coeff_all_pairs', Integer)
    instability_index = Column('instability_index', Float)
    molecules_per_cell = Column('molecules_per_cell', Integer)
         
    __mapper_args__ = {'polymorphic_identity': "PROTEIN",
                       'inherit_condition': id == Bioentity.id}
    
    @hybrid_property
    def search_entry_title(self):
        return self.full_name_with_link
    @hybrid_property
    def search_entry(self):
        entry = ''
        if len(self.aliases) > 0:
            entry = '<span class="muted">Aliases: ' + self.alias_str + '</span><br>'
        return entry
    @hybrid_property
    def search_entry_type(self):
        return 'Protein'
    
    def get_percent_aa(self, aa_abrev):
        return "{0:.2f}".format(100*float(getattr(self, aa_abrev))/self.length) + '%'

    def __init__(self, bioent_id, display_name, format_name, 
                 transcript_id, 
                 molecular_weight, pi, cai, length, n_term_seq, c_term_seq,
                 codon_bias, fop_score, gravy_score, aromaticity_score, 
                 ala, arg, asn, asp, cys, gln, glu, gly, his, ile, leu, lys, met, phe, pro, thr, ser, trp, tyr, val, 
                 aliphatic_index, atomic_comp_H, atomic_comp_S, atomic_comp_N, atomic_comp_O, atomic_comp_C,
                 half_life_yeast_in_vivo, half_life_ecoli_in_vivo, half_life_mammalian_reticulocytes_in_vitro,
                 extinction_coeff_no_cys_residues_as_half_cystines, extinction_coeff_all_cys_residues_reduced,
                 extinction_coeff_all_cys_residues_appear_as_half_cystines, extinction_coeff_all_cys_pairs_form_cystines,
                 instability_index, molecules_per_cell,
                 date_created, created_by):
        Bioentity.__init__(self, bioent_id, display_name, format_name, 'PROTEIN', None, 'SGD', None, date_created, created_by)
        self.transcript_id = transcript_id
        
        self.molecular_weight = molecular_weight
        self.pi = pi
        self.cai = cai
        self.length = length
        self.n_term_seq = n_term_seq
        self.c_term_seq = c_term_seq
        self.codon_bias = codon_bias
        self.fop_score = fop_score
        self.gravy_score = gravy_score
        self.aromaticity_score = aromaticity_score
        
        self.ala = ala
        self.arg = arg
        self.asn = asn
        self.asp = asp
        self.cys = cys
        self.gln = gln
        self.glu = glu
        self.gly = gly
        self.his = his
        self.ile = ile
        self.leu = leu
        self.lys = lys
        self.met = met
        self.phe = phe
        self.pro = pro
        self.thr = thr
        self.ser = ser
        self.trp = trp
        self.tyr = tyr
        self.val = val
        
        self.aliphatic_index = aliphatic_index
        self.atomic_comp_H = atomic_comp_H
        self.atomic_comp_S = atomic_comp_S
        self.atomic_comp_N = atomic_comp_N
        self.atomic_comp_O = atomic_comp_O
        self.atomic_comp_C = atomic_comp_C
        self.half_life_yeast_in_vivo = half_life_yeast_in_vivo
        self.half_life_ecoli_in_vivo = half_life_ecoli_in_vivo
        self.half_life_mammalian_reticulocytes_in_vitro = half_life_mammalian_reticulocytes_in_vitro
        self.extinction_coeff_all_cys_pairs_form_cystines = extinction_coeff_all_cys_pairs_form_cystines
        self.extinction_coeff_all_cys_residues_as_half_cystines  = extinction_coeff_all_cys_residues_appear_as_half_cystines
        self.extinction_coeff_all_cys_residues_reduced = extinction_coeff_all_cys_residues_reduced
        self.extinction_coeff_no_cys_residues_as_half_cystines = extinction_coeff_no_cys_residues_as_half_cystines
        self.instability_index = instability_index
        self.molecules_per_cell = molecules_per_cell
        
class Bioentevidence(Evidence):
    __tablename__ = "bioentevidence" 
    
    id = Column('evidence_id', Integer, ForeignKey(Evidence.id), primary_key=True)
    topic = Column('topic', String)
    bioent_id = Column('bioent_id', Integer, ForeignKey(Gene.id))
    type = 'BIOENT_EVIDENCE'  
    
    #Relationships 
    gene = relationship(Gene, uselist=False)
    
    __mapper_args__ = {'polymorphic_identity': "BIOENT_EVIDENCE",
                       'inherit_condition': id==Evidence.id}

    def __init__(self, evidence_id, reference_id, topic,
                bioent_id, date_created, created_by):
        Evidence.__init__(self, evidence_id, None, reference_id, 'BIOENT_EVIDENCE', None, 'SGD', date_created, created_by)
        self.topic = topic
        self.bioent_id = bioent_id
        
        