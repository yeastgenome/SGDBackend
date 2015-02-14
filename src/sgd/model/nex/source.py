__author__ = 'kelley'

class Source(Base, EqualityByIDMixin, UpdateByJsonMixin):
    __tablename__ = 'source'

    id = Column('source_id', Integer, primary_key = True)
    display_name = Column('display_name', String)
    format_name = Column('format_name', String)
    link = Column('obj_url', String)
    bud_id = Column('bud_id', Integer)
    description = Column('description', String)
    date_created = Column('date_created', Date, server_default=FetchedValue())
    created_by = Column('created_by', String, server_default=FetchedValue())
    link = None

    __eq_values__ = ['id', 'display_name', 'format_name', 'description', 'date_created', 'created_by']
    __eq_fks__ = []

    def __init__(self, obj_json):
        UpdateByJsonMixin.__init__(self, obj_json)
        self.format_name = create_format_name(self.display_name)

    def unique_key(self):
        return self.format_name


DROP TABLE SOURCE CASCADE CONSTRAINTS;
CREATE TABLE SOURCE (
SOURCE_ID INTEGER NOT NULL,
FORMAT_NAME VARCHAR2(100) NOT NULL,
DISPLAY_NAME VARCHAR2(500) NOT NULL,
OBJ_URL VARCHAR2(500),
BUD_ID INTEGER NULL,
DESCRIPTION VARCHAR2(400) NULL,
DATE_CREATED DATE DEFAULT SYSDATE NOT NULL,
CREATED_BY VARCHAR2(12) DEFAULT SUBSTR(USER,1,12) NOT NULL,
CONSTRAINT SOURCE_PK PRIMARY KEY (SOURCE_ID),
CONSTRAINT SOURCE_UK UNIQUE (FORMAT_NAME) ) TABLESPACE DATA01;
GRANT SELECT ON SOURCE TO DBSELECT;
GRANT INSERT, SELECT, UPDATE ON SOURCE TO CURATOR;
GRANT DELETE, INSERT, SELECT, UPDATE ON SOURCE TO AUXILIARY;