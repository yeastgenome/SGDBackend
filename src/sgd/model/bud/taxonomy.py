from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.bud import Base


class Taxonomy(Base, EqualityByIDMixin):
    __tablename__ = 'taxonomy'

    id = Column('taxon_id', Integer, primary_key = True)
    name = Column('tax_term', String)
    common_name = Column('common_name', String)
    rank = Column('rank', String)
    
    def __repr__(self):
        data = self.name, self.common_name, self.rank
        return 'Taxonomy(name=%s, common_name=%s, rank=%s)' % data