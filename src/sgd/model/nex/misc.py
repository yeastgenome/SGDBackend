from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, FetchedValue
from sqlalchemy.types import Integer, String, Date

from src.sgd.model import EqualityByIDMixin
from src.sgd.model.nex import Base, create_format_name


__author__ = 'kpaskov'

class Experiment(Base, EqualityByIDMixin):
    __tablename__ = 'experiment'

    id = Column('experiment_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    description = Column('description', String)
    eco_id = Column('eco_id', String)
    category = Column('category', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    def __init__(self, display_name, source, description, eco_id, date_created, created_by):
        self.display_name = display_name
        self.format_name = create_format_name(display_name)
        self.link = None
        self.source_id = source.id
        self.description = description
        self.eco_id = eco_id
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return self.format_name

    def to_json(self):
        return {
            'format_name': self.format_name,
            'display_name': self.display_name,
            'link': self.link,
            'id': self.id,
            }

class Strain(Base, EqualityByIDMixin):
    __tablename__ = 'strain'

    id = Column('strain_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    description = Column('description', String)
    is_alternative_reference = Column('is_alternative_reference', Integer)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    def __init__(self, display_name, source, description, is_alternative_reference, date_created, created_by):
        self.display_name = display_name
        self.format_name = create_format_name(display_name).replace('.', '')
        self.link = None
        self.source_id = source.id
        self.description = description
        self.is_alternative_reference = is_alternative_reference
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return self.format_name

    def to_json(self):
        return {
            'display_name': self.display_name,
            'description': self.description,
            'id': self.id,
            'link': self.link
            }

class Source(Base, EqualityByIDMixin):
    __tablename__ = 'source'

    id = Column('source_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    def __init__(self, display_name, description, date_created, created_by):
        self.display_name = display_name
        self.format_name = create_format_name(display_name)
        self.description = description
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return self.format_name

    def to_json(self):
        return self.display_name
       
class Url(Base, EqualityByIDMixin):
    __tablename__ = 'url'
    id = Column('url_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer)
    category = Column('category', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"URL"}

    def __init__(self, display_name, format_name, class_type, link, source, category, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.category = category
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return (self.link, self.format_name)

    def to_json(url):
        return {
            'display_name': url.display_name,
            'link': url.link,
            }

class Alias(Base, EqualityByIDMixin):
    __tablename__ = 'alias'

    id = Column('alias_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    link = Column('obj_url', String)
    source_id = Column('source_id', Integer, ForeignKey(Source.id))
    category = Column('category', String)
    date_created = Column('date_created', Date)
    created_by = Column('created_by', String)

    #Relationships
    source = relationship(Source, uselist=False)

    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"ALIAS"}

    def __init__(self, display_name, format_name, class_type, link, source, category, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.link = link
        self.source_id = source.id
        self.category = category
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return (self.display_name, self.format_name)

    def to_json(self):
        return {
                'id': self.id,
                'display_name': self.display_name,
                'link': self.link,
                'source': self.source.to_json(),
                'category': self.category
               }

class Relation(Base, EqualityByIDMixin):
    __tablename__ = 'relation'

    id = Column('relation_id', Integer, primary_key=True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    class_type = Column('class', String)
    source_id = Column('source_id', Integer, ForeignKey('nex.source.source_id'))
    relation_type = Column('relation_type', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())

    __mapper_args__ = {'polymorphic_on': class_type,
                       'polymorphic_identity':"RELATION"}

    def __init__(self, display_name, format_name, class_type, source, relation_type, date_created, created_by):
        self.display_name = display_name
        self.format_name = format_name
        self.class_type = class_type
        self.source_id = source.id
        self.relation_type = relation_type
        self.date_created = date_created
        self.created_by = created_by

    def unique_key(self):
        return (self.format_name, self.class_type, self.relation_type)

class Experimentrelation(Relation):
    __tablename__ = 'experimentrelation'

    id = Column('relation_id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey(Experiment.id))
    child_id = Column('child_id', Integer, ForeignKey(Experiment.id))

    #Relationships
    parent = relationship(Experiment, uselist=False, backref="children", primaryjoin="Experimentrelation.parent_id==Experiment.id")
    child = relationship(Experiment, uselist=False, backref="parents", primaryjoin="Experimentrelation.child_id==Experiment.id")

    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT',
                       'inherit_condition': id == Relation.id}

    def __init__(self, source, relation_type, parent, child, date_created, created_by):
        Relation.__init__(self, parent.format_name + '_' + child.format_name,
                          child.display_name + ' ' + ('' if relation_type is None else relation_type + ' ') + parent.display_name,
                          'EXPERIMENT', source, relation_type, date_created, created_by)
        self.parent_id = parent.id
        self.child_id = child.id

class Experimentalias(Alias):
    __tablename__ = 'experimentalias'

    id = Column('alias_id', Integer, primary_key=True)
    experiment_id = Column('experiment_id', Integer, ForeignKey(Experiment.id))

    experiment = relationship(Experiment, uselist=False)

    __mapper_args__ = {'polymorphic_identity': 'EXPERIMENT',
                       'inherit_condition': id == Alias.id}

    def __init__(self, display_name, source, category, experiment, date_created, created_by):
        Alias.__init__(self, display_name, experiment.format_name, 'EXPERIMENT', None, source, category, date_created, created_by)
        self.experiment_id = experiment.id