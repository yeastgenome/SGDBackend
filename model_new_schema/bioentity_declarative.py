'''
Created on Nov 6, 2012

@author: kpaskov

This is some test code to experiment with working with SQLAlchemy - particularly the Declarative style. These classes represent what 
will eventually be the Bioentity classes/tables in the new SGD website schema. This code is currently meant to run on the KPASKOV 
schema on fasolt.
'''
from model_new_schema import Base, subclasses, \
    CommonEqualityMixin, metadata, engine
from model_new_schema.bioconcept import Bioconcept
from model_new_schema.biorelation import Biorelation
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.expression import select
from sqlalchemy.types import Integer, String, Date, Float
import datetime
import model_new_schema
    
class Bioentity(Base, CommonEqualityMixin):
    __tablename__ = "bioent"
    
    id = Column('bioent_id', Integer, primary_key=True)
    name = Column('name', String)
    type = Column('bioent_type', String)
    dbxref = Column('dbxref', String)
    source = Column('source', String)
    #locus_id = Column('locus_id', Integer, ForeignKey('biocon.biocon_id'))
    #strain_id = Column('strain_id', Integer, ForeignKey('biocon.biocon_id'))
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    
    __mapper_args__ = {'polymorphic_on': type,
                       'polymorphic_identity':"BIOENTITY"}
    
    biorel_source = relationship(Biorelation, primaryjoin="Biorelation.sink_bioent_id==Bioentity.id")
    biorel_sink = relationship(Biorelation, primaryjoin="Biorelation.source_bioent_id==Bioentity.id")
    
    #locus = relationship(Bioconcept, primaryjoin='Bioconcept.id==Bioentity.locus_id')
    #strain = relationship(Bioconcept, primaryjoin='Bioconcept.id==Bioentity.strain_id')

    #bioconcepts = relationship(Bioconcept, secondary=bioent_biocon_map, backref='bioentities')
    
    bioent_biocon = relationship('BioentBiocon', collection_class=attribute_mapped_collection('bioconcept'))
    bioconcept_evidence = association_proxy('bioent_biocon', 'evidences')
    
    @hybrid_property
    def biorelation(self):
        return self.biorel_source + self.biorel_sink
       
    @hybrid_property
    def bioconcept(self):
        return self.bioconcept_evidence.keys()
    
    def __init__(self, name, bioent_type, taxon_id, dbxref, source, locus, strain):
        self.name = name
        self.type = bioent_type
        self.taxon_id = taxon_id
        self.dbxref = dbxref
        self.source = source
        self.locus = locus
        self.strain = strain
        self.created_by = model_new_schema.current_user
        self.date_created = datetime.datetime.now()
        
        self.bioconcepts.add(locus)
        self.bioconcepts.add(strain)
    
    def __repr__(self):
        data = self.__class__.__name__, self.id, self.name
        return '%s(id=%s, name=%s)' % data
    
    def __getattr__(self, name):
        if name.endswith('_evidence'):
            name = name[:-9].upper()
            evidence = True
        else:
            name = name.upper()
            evidence = False;

        return self.__get_objects_for_subclass__(name, evidence)
    
    def __get_objects_for_subclass__(self, subclass_name, evidence=False):
        if subclass_name in subclasses(Biorelation):
            return filter(lambda x: x.type == subclass_name, self.biorelation)
        elif subclass_name in subclasses(Bioconcept):
            if evidence:
                return dict((k, v) for k, v in self.bioconcept_evidence.iteritems() if k.type == subclass_name)
            else:
                return filter(lambda x: x.type == subclass_name, self.bioconcept)
        raise AttributeError()

class Gene(Bioentity):
    __tablename__ = "gene"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    #gene_name = Column('gene_name', String)
    
    __mapper_args__ = {'polymorphic_identity': "GENE",
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, name, bioent_type, taxon_id, dbxref, source, gene_name):
        super(Bioentity, self).__init__(name, bioent_type, taxon_id, dbxref, source)
        self.gene_name = gene_name
        
class Protein(Bioentity):
    __tablename__ = "protein"
    
    id = Column('bioent_id', Integer, ForeignKey(Bioentity.id), primary_key=True)
    molecular_weight = Column('molecular_weight', Integer)
    pi = Column('pi', Float)
    cai = Column('cai', Float)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)
    gene_id = Column('gene_id', Integer, ForeignKey('gene.bioent_id'))
    
    #Relationships
    #gene = relationship('Gene', backref='proteins')
    
    __mapper_args__ = {'polymorphic_identity': "PROTEIN",
                       'inherit_condition': id == Bioentity.id}
    
    def __init__(self, name, bioent_type, taxon_id, dbxref, source):
        super(Bioentity, self).__init__(name, bioent_type, taxon_id, dbxref, source)
        
#Gene Subclasses
gene_subclass_names = {'TRNA', 'SNORNA', 'RRNA', 'NCRNA', 'SNRNA'}

for gene_subclass_name in gene_subclass_names:
    class_name = gene_subclass_name.capitalize()
    globals()[class_name] = type(class_name, (Gene,), {'__mapper_args__':{'polymorphic_identity': gene_subclass_name}}).__class__

#All other subclasses of Bioentity.
result = engine.connect().execute(select([Bioentity.type]).distinct())
for row in result:
    try:
        bioent_type = str(row['bioent_type'])
        locals()[bioent_type.capitalize()]
    except:
        type(bioent_type.capitalize(), (Bioentity,), {'__mapper_args__':{'polymorphic_identity': bioent_type}})


    
