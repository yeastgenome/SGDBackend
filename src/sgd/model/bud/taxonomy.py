from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date
from sqlalchemy.orm import relationship, backref

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base


class Taxonomy(Base, EqualityByIDMixin):
    __tablename__ = 'taxonomy'

    id = Column('taxon_id', Integer, primary_key = True)
    name = Column('tax_term', String)
    common_name = Column('common_name', String)
    rank = Column('rank', String)
    created_by = Column('created_by', String)
    date_created = Column('date_created', Date)
    
    def __repr__(self):
        data = self.name, self.common_name, self.rank
        return 'Taxonomy(name=%s, common_name=%s, rank=%s)' % data


class TaxonomyRelation(Base, EqualityByIDMixin):
    __tablename__ = 'tax_relationship'

    id = Column('tax_relationship_no', Integer, primary_key=True)
    parent_id = Column('parent_taxon_id', Integer, ForeignKey(Taxonomy.id))
    child_id = Column('child_taxon_id', Integer, ForeignKey(Taxonomy.id))
    generation = Column('generation', Integer)

    #Relationships
    parent = relationship(Taxonomy, backref=backref("children", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[parent_id])
    child = relationship(Taxonomy, backref=backref("parents", cascade="all, delete-orphan", passive_deletes=True), uselist=False, foreign_keys=[child_id])

class TaxonomyAlias(Base, EqualityByIDMixin):
    __tablename__ = 'tax_synonym'

    id = Column('tax_synonym_no', Integer, primary_key=True)
    taxon_id = Column('taxon_id', Integer, ForeignKey(Taxonomy.id))
    synonym = Column('tax_synonym', String)

    #Relationships
    taxonomy = relationship(Taxonomy, uselist=False)
