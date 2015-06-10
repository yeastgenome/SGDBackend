__author__ = 'kkarra'


class HistoryAnnotation(Base, EqualityByIDMixin):
   __tablename__ = 'historyannotation'

   id = Column('annotation_id', Integer, primary_key=True)
   bud_id = Column('bud_id', Integer)
   colleague_id = Column('colleague_id', Integer)
   created_by = Column('created_by', String)
   date_annotation_made = Column('date_annotation_made', Date)
   date_created = Column('date_created', Date)
   dbentity_id = Column('dbentity_id', Integer)
   history_type = Column('history_type', String)
   history_note = Column('history_note', String)
   reference_id = Column('reference_id', Integer)
   source_id = Column('source_id', Integer)
   subclass = Column('subclass', String)
   taxonomy_id = Column('taxonomy_id', Integer)

   __eq_values__ = ['id', 'display_name', 'format_name', 'link', 'bud_id', 'created_by', 'date_created']
   __eq_fks__ = [('source', Source, False)]
   __id_values__ = ['format_name', 'id']
   __no_edit_values__ = ['id', 'format_name', 'link', 'date_created', 'created_by']
   __filter_values__ = []

    def __init__(self, obj_json, session):
        UpdateWithJsonMixin.__init__(self, obj_json, session)

    def to_json(self):
        obj_json = ToJsonMixin.to_json(self)
        return obj_json

    def to_semi_json(self):
        return self.to_min_json()