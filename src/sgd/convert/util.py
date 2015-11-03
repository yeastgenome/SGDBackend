from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import not_
from src.sgd.convert.gpad_config import curator_id, computational_created_by,  \
    go_db_code_mapping, go_ref_mapping, current_go_qualifier, email_receiver, \
    email_subject


from src.sgd.convert.config import log_directory

__author__ = 'kpaskov; sweng66'

def prepare_schema_connection(model_cls, dbtype, dbhost, dbname, schema, dbuser, dbpass):
    class Base(object):
        __table_args__ = {'schema': schema, 'extend_existing':True}

    model_cls.Base = declarative_base(cls=Base)
    model_cls.Base.schema = schema
    model_cls.metadata = model_cls.Base.metadata
    engine_key = "%s://%s:%s@%s/%s" % (dbtype, dbuser, dbpass, dbhost, dbname)
    engine = create_engine(engine_key, pool_recycle=3600)
    model_cls.Base.metadata.bind = engine
    session_maker = sessionmaker(bind=engine)

    return session_maker

def create_format_name(display_name):
    format_name = display_name.replace(' ', '_')
    format_name = format_name.replace('/', '-')
    return format_name

def float_approx_equal(x, y, tol=1e-18, rel=1e-7):
    #http://code.activestate.com/recipes/577124-approximately-equal/
    if tol is rel is None:
        raise TypeError('cannot specify both absolute and relative errors are None')
    tests = []
    if tol is not None: tests.append(tol)
    if rel is not None: tests.append(rel*abs(x))
    assert tests
    return abs(x - y) <= max(tests)

def break_up_file(filename, delimeter='\t'):
    rows = []
    f = open(filename, 'r')
    for line in f:
        rows.append(line.split(delimeter))
    f.close()
    return rows

def is_number(str_value):
    try:
        int(str_value)
        return True
    except:
        return False

def read_gpad_file(filename, bud_session, nex_session, uniprot_to_date_assigned, uniprot_to_sgdid_list, get_extension=None, get_support=None):

    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.locus import Locus
    from src.sgd.model.nex.go import Go
    from src.sgd.model.nex.eco import EcoAlias

    from src.sgd.model.bud.go import Go as Go_bud 
    
    from src.sgd.model import nex
    from src.sgd.convert import config

    goid_to_go_id = dict([(x.goid, x.id) for x in nex_session.query(Go).all()])
    evidence_to_eco_id = dict([(x.display_name, x.eco_id) for x in nex_session.query(EcoAlias).all()])

    pmid_to_reference_id = {}
    sgdid_to_reference_id = {}
    for x in nex_session.query(Reference).all():
        pmid_to_reference_id[x.pmid] = x.id
        sgdid_to_reference_id[x.sgdid] = x.id

    sgdid_to_locus_id = dict([(x.sgdid, x.id) for x in nex_session.query(Locus).all()])

    f = open(filename)
    
    read_line = {}
    bad_ref = []

    data = []

    for line in f:

        if line.startswith('!'):
            continue

        field = line.strip().split('\t')
        if field[9] != 'SGD' and not field[11].startswith('go_evidence=IEA'):
            continue

        ## get rid of duplicate lines...                                                                    
        if line in read_line:
            continue
        read_line[line] = 1

        if get_extension == 1 and field[10] == '':
            continue
        if get_support == 1 and field[6] == '':
            continue

        ## uniprot ID & SGDIDs                                                                              
        uniprotID = field[1]
        sgdid_list = uniprot_to_sgdid_list.get(uniprotID)
        if sgdid_list is None:
            print "The UniProt ID = ", uniprotID, " is not mapped to any SGDID."
            continue

        ## go_qualifier                                                                                     
        go_qualifier = field[2]
        if go_qualifier == 'part_of':
            go_qualifier = 'part of'
        if go_qualifier == 'involved_in':
            go_qualifier = 'involved in'
        if 'NOT' in go_qualifier:
            go_qualifier = 'NOT'

        ## go_id                                                                                            
        goid = field[3]
        go_id = goid_to_go_id.get(goid)
        if go_id is None:
            print "The GOID = ", goid, " is not in GO table."
            continue

        ## eco_id                                                                                           
        # go_evidence=IMP|id=2113463881|curator_name=Kimberly Van Auken                                     
        annot_prop_dict = annot_prop_to_dict(field[11])
        go_evidence = annot_prop_dict.get('go_evidence')
        eco_id = evidence_to_eco_id.get(go_evidence)
        if eco_id is None:
            print "The go_evidence = ", annotation.go_evidence, " is not in the ECO table."
            continue

        ## source                                                                                           
        source = field[9]

        ## created_by                                                                                       
        if source != 'SGD' and go_evidence == 'IEA':
            created_by = computational_created_by
        else:
            created_by = curator_id.get(annot_prop_dict.get('curator_name'))

        ## reference_id                                                                                     
        reference_id = None
        if field[4].startswith('PMID:'):
            pmid = field[4][5:]    # PMID:1234567; need to be 1234567                                       
            reference_id = pmid_to_reference_id.get(int(pmid))
        else:
            ref_sgdid = go_ref_mapping.get(field[4])
            if ref_sgdid is None:
                if field[4] not in bad_ref:
                    bad_ref.append(field[4])
                print "UNKNOWN REF: ", field[4], ", line=", line
                continue
            reference_id = sgdid_to_reference_id.get(ref_sgdid)
        if reference_id is None:
            print "The PMID = " + str(pmid) + " is not in the REFERENCEDBENTITY table."
            continue

        # assigned_group = field[9]           
        # eg, SGD for manual cuartion;
        # Interpro, UniPathway, UniProtKB, GOC, RefGenome for computational annotation
        # taxon_id = field[7]                  
        
        date_created = str(field[8][0:4]) + '-' + str(field[8][4:6]) + '-' + str(field[8][6:])
        if source == 'SGD':
            date_assigned = uniprot_to_date_assigned.get(uniprotID)
            annotation_type = 'manually curated'
        else:
            date_assigned = date_created
            annotation_type = 'computational'
        
        sgdid_list = uniprot_to_sgdid_list.get(uniprotID)
        if sgdid_list is None:
            print "UniProt ID ", uniprotID, " is not in GPI file."
            continue

        for sgdid in sgdid_list:
            if sgdid == '':
                continue
            locus_id = sgdid_to_locus_id.get(sgdid)
            if locus_id is None:
                print "The sgdid = ", sgdid, " is not in LOCUSDBENTITY table."
                continue
    
            entry = { 'source': source,
                      'dbentity_id': locus_id,
                      'reference_id': reference_id,
                      'go_id': go_id,
                      'eco_id': eco_id,
                      'annotation_type': annotation_type,
                      'go_qualifier': go_qualifier,
                      'date_assigned': date_assigned,
                      'date_created': date_created,
                      'created_by': created_by } 
        
            if get_extension == 1:
                entry['goextension'] = field[10]
            if get_support == 1:
                entry['gosupport'] = field[6]

            data.append(entry)
       
    return data

def annot_prop_to_dict(annot_prop):

    annot_prop_dict = {}
    for annot_prop in annot_prop.split('|'):
        annot = annot_prop.split('=')
        annot_prop_dict[annot[0]] = annot[1]
    return annot_prop_dict
        
def read_gpi_file(filename):

    f = open(filename)

    uniprot_to_date_assigned = {}
    uniprot_to_sgdid_list = {}
    for line  in f:

        if line.startswith('!'):
            continue

        field = line.strip().split('\t')

        if len(field) < 10:
            continue

        # same uniprot ID for multiple RNA entries                                                  
        
        uniprotID = field[1]
        sgdid = field[8].replace('SGD:', '')
        sgdid_list = [] if uniprot_to_sgdid_list.get(uniprotID) is None else uniprot_to_sgdid_list.get(uniprotID)
        sgdid_list.append(sgdid)
        uniprot_to_sgdid_list[uniprotID] = sgdid_list

        for pair in field[9].split('|'):
            if not pair.startswith('go_annotation_complete'):
                continue
            property = pair.split('=')
            date = property[1]
            uniprot_to_date_assigned[uniprotID] = str(date[0:4]) + '-' + str(date[4:6]) + '-' + str(date[6:])

    f.close()

    return [uniprot_to_date_assigned, uniprot_to_sgdid_list]

def get_go_extension_link(dbxref_id):

    if dbxref_id.startswith('SGD:S'):
        sgdid = dbxref_id.replace('SGD:', '')
        return "/locus/" + sgdid + "/overview"
    if dbxref_id.startswith('GO:'):
        return "http://amigo.geneontology.org/amigo/term/" + dbxref_id
    if dbxref_id.startswith('UniProtKB:'):
        uniprotID = dbxref_id.replace('UniProtKB:', '')
        return "http://www.uniprot.org/uniprot/" + uniprotID
    if dbxref_id.startswith('CHEBI:'):
        return "http://www.ebi.ac.uk/chebi/searchId.do?chebiId=" + dbxref_id
    if dbxref_id.startswith('SO:'):
        return "http://www.sequenceontology.org/browser/current_svn/term/" + dbxref_id
    if dbxref_id.startswith('RNAcentral:'):
        id = dbxref_id.replace('RNAcentral:', '')
        return "http://rnacentral.org/rna/" + id
    if dbxref_id.startswith('UniProtKB-KW:'):
        id = dbxref_id.replace('UniProtKB-KW:', '')
        return "http://www.uniprot.org/keywords/" + id
    if dbxref_id.startswith('UniProtKB-SubCell:'):
        id = dbxref_id.replace('UniProtKB-SubCell:', '')
        return "http://www.uniprot.org/locations/" + id
    if dbxref_id.startswith('InterPro:'):
        id = dbxref_id.replace('InterPro:', '')
        return "http://www.ebi.ac.uk/interpro/entry/" + id
    if dbxref_id.startswith('EC:'):
        EC = dbxref_id.replace('EC:', ' ')
        return "http://enzyme.expasy.org/EC/" + EC
    if dbxref_id.startswith('UniPathway:'):
        id = dbxref_id.replace('UniPathway:', '')
        return "http://www.grenoble.prabi.fr/obiwarehouse/unipathway/upa?upid=" + id
    if dbxref_id.startswith('HAMAP:'):
        id = dbxref_id.replace('HAMAP:', '')
        return "http://hamap.expasy.org/unirule/" + id
    if dbxref_id.startswith('protein_id:'):
        id = dbxref_id.replace('protein_id:', '')
        return "http://www.ncbi.nlm.nih.gov/protein/" + id
    if dbxref_id.startswith('EMBL:'):
        id = dbxref_id.replace('EMBL:', '')
        return "http://www.ebi.ac.uk/Tools/dbfetch/emblfetch?style=html&id=" + id
    if dbxref_id.startswith('MGI:'):
        id = dbxref_id.replace('MGI:', '')
        return "http://uswest.ensembl.org/Drosophila_melanogaster/Gene/Summary?g=" + id
    if dbxref_id.startswith('PANTHER:'):
        id = dbxref_id.replace('PANTHER:', '')
        return "http://pantree.org/node/annotationNode.jsp?id=" + id
    return "Unknown"

def children_from_obo(filename, ancestor):
    f = open(filename, 'r')
    child = ''
    parent_to_children = {}
    id_to_rank = {}
    for line in f:
        line = line.strip()
        pieces = line.split(': ')
        if pieces[0] == 'id':
            child = pieces[1]
        if pieces[0] == 'is_a':
            parent = pieces[1].split(' ')[0]
            if parent not in parent_to_children:
                parent_to_children[parent] = []
            parent_to_children[parent].append(child)
        if pieces[0] == 'property_value' and pieces[1].startswith('has_rank NCBITaxon:'):
            # id_to_rank[child] = pieces[1].replace("has_rank NCBITaxon:", "") 
            id_to_rank[child] = pieces[1].replace("has_rank ", "")   

    # do breadth first search of parent_to_children
    # populate filtered_parent_set
    filtered_parent_set = []
    working_set = []
    working_set.append(ancestor)
    filtered_id_to_rank = {}
    while len(working_set) > 0:
        current = working_set[0]
        working_set = working_set[1:]
        filtered_parent_set.append(current)
        filtered_id_to_rank[current] = id_to_rank.get(current)
        if current in parent_to_children:
            for child in parent_to_children[current]:
                if child not in filtered_parent_set:
                    working_set.append(child)
        
    return [filtered_parent_set, filtered_id_to_rank]


def read_obo(ontology, filename, key_switch, parent_to_children, is_obsolete_id, source, alias_source=None):
    terms = []
    f = open(filename, 'r')    
    term = None
    id_name = key_switch.get('id')
    if id_name is None:
        id_name = key_switch.get('xref')
    is_obsolete_ecoid = {}
    id_to_id = {}
    parent_child_pair = {}
    for line in f:
        line = line.strip()
        ## remove all back slashes
        line = line.replace("\\", "")
        if ontology != 'RO' and line == '[Typedef]':
            break
        if ontology == 'OBI' and (line.startswith('property_value:') or line.startswith('owl-')):
            continue
        if line == '[Term]' or line == '[Typedef]':
            if term is not None:
                terms.append(term)
            if alias_source is None:
                term = { 'source': { 'display_name': source } }
            else:
                term = { 'aliases': [],
                         'urls': [],
                         'source': { 'display_name': source } }

        elif term is not None:
            pieces = line.split(': ')
            if ontology == 'RO' and pieces[0] == 'id':
                id = pieces[1]
            if len(pieces) >= 2:
                if alias_source and pieces[0] == 'synonym':
                    if len(pieces) > 2:
                        pieces.pop(0)
                        synonym_line = ": ".join(pieces)
                    else:
                        synonym_line = pieces[1]
                    quotation_split = synonym_line.split('"')
                    alias_name = quotation_split[1]
                    type = quotation_split[2].split('[')[0].strip()
                    alias_type = type.split(' ')[0]
                    if ontology == 'CHEBI':
                        alias_type = type[:40]
                        if alias_type not in ('EXACT', 'RELATED', 'EXACT IUPAC_NAME'):
                            continue
                        if alias_type == 'EXACT IUPAC_NAME':
                            alias_type = 'IUPAC name'
                        if len(alias_name) >= 500 or (alias_name, alias_type) in [(x['display_name'], x['alias_type']) for x in term['aliases']]:
                            continue                  
                    term['aliases'].append({'display_name': alias_name, "alias_type": alias_type, "source": {"display_name": alias_source}})
                elif ontology == 'GO' and (pieces[0] == 'is_a' or pieces[0] == 'relationship'):
                    if term.get('display_name') is None:
                        continue
                    # is_a: GO:0051231 ! spindle elongation
                    # relationship: part_of GO:0015767 ! lactose transport
                    parent = pieces[1].split('!')[0].strip()
                    relation_type = 'is a'
                    if pieces[0] == 'relationship':
                        type_goid = parent.split(' ')
                        relation_type = type_goid[0].replace('_', ' ')
                        parent = type_goid[1].strip()
                    if (parent, term['goid']) in parent_child_pair:
                        continue
                    parent_child_pair[(parent, term['goid'])] = 1
                    ro_id = get_relation_to_ro_id(relation_type)
                    if ro_id is None:
                        print relation_type, " is not in RO table"
                        continue
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    parent_to_children[parent].append({id_name: term[id_name], 'display_name': term['display_name'], key_switch['namespace']: term[key_switch['namespace']],'source': {'display_name': source}, 'ro_id': ro_id})
                elif pieces[0] == 'is_a' and term.get('display_name') and term.get(id_name):
                    parent = pieces[1].split('!')[0].strip()
                    if parent not in parent_to_children:
                        parent_to_children[parent] = []
                    if id_name == 'roid':
                        parent_to_children[parent].append({id_name: term[id_name], 'display_name': term['display_name'], 'source': {'display_name': source}, 'relation_type': 'is a'})
                    elif key_switch.get('namespace'):
                        parent_to_children[parent].append({id_name: term[id_name], 'display_name': term['display_name'], key_switch['namespace']: term[key_switch['namespace']], 'source': {'display_name': source}, 'ro_id': get_relation_to_ro_id('is a')})
                    else:
                        parent_to_children[parent].append({id_name: term[id_name], 'display_name': term['display_name'], 'source': {'display_name': source}, 'ro_id': get_relation_to_ro_id('is a')})
                elif pieces[0] in key_switch:
                    text = pieces[1]
                    key = pieces[0]
                    if ontology == 'RO':
                        if pieces[0] == 'xref':
                            id_to_id[pieces[1]] = id
                            id = ''
                        elif pieces[0] == 'name':
                            text = text.replace("_", " ")
                    if ontology == 'GO' and pieces[0] == 'namespace':
                        text = text.replace("_", " ")
                    if pieces[0] == 'def':
                        defline = pieces[1]
                        if len(pieces) > 2:
                            pieces.pop(0)
                            defline = ": ".join(pieces) 
                        quotation_split = defline.split('" [')
                        text = quotation_split[0][1:]
                        text = text.replace("\\", "")
                    term[key_switch[key]] = text
                elif pieces[0] == 'is_obsolete':
                    is_obsolete_id[term[id_name]] = 1

    if term is not None:
        terms.append(term)

    f.close()
    if ontology == 'RO':
        return [terms, id_to_id]
    else:
        return terms


def clean_up_orphans(nex_session_maker, child_cls, parent_cls, class_type):
    nex_session = nex_session_maker()
    child_table_ids = nex_session.query(child_cls.id).subquery()
    query = nex_session.query(parent_cls).filter_by(class_type=class_type).filter(not_(parent_cls.id.in_(child_table_ids)))
    deleted_count = query.count()
    query.delete(synchronize_session=False)
    nex_session.commit()
    nex_session.close()
    return deleted_count

word_to_dbentity_id = None

number_to_roman = {'01': 'I', '1': 'I',
                   '02': 'II', '2': 'II',
                   '03': 'III', '3': 'III',
                   '04': 'IV', '4': 'IV',
                   '05': 'V', '5': 'V',
                   '06': 'VI', '6': 'VI',
                   '07': 'VII', '7': 'VII',
                   '08': 'VIII', '8': 'VIII',
                   '09': 'IX', '9': 'IX',
                   '10': 'X',
                   '11': 'XI',
                   '12': 'XII',
                   '13': 'XIII',
                   '14': 'XIV',
                   '15': 'XV',
                   '16': 'XVI',
                   '17': 'Mito',
                   }

def get_word_to_dbentity_id(word, nex_session):
    from src.sgd.model.nex.locus import Locus

    global word_to_dbentity_id
    if word_to_dbentity_id is None:
        word_to_dbentity_id = {}
        for locus in nex_session.query(Locus).all():
            word_to_dbentity_id[locus.format_name.lower()] = locus.id
            word_to_dbentity_id[locus.display_name.lower()] = locus.id
            word_to_dbentity_id[locus.format_name.lower() + 'p'] = locus.id
            word_to_dbentity_id[locus.display_name.lower() + 'p'] = locus.id

    word = word.lower()
    return None if word not in word_to_dbentity_id else word_to_dbentity_id[word]

def get_dbentity_by_name(dbentity_name, to_ignore, nex_session):
    from src.sgd.model.nex.locus import Locus
    if dbentity_name not in to_ignore:
        try:
            int(dbentity_name)
        except ValueError:
            dbentity_id = get_word_to_dbentity_id(dbentity_name, nex_session)
            return None if dbentity_id is None else nex_session.query(Locus).filter_by(id=dbentity_id).first()
    return None

def link_gene_names(text, to_ignore, nex_session):
    words = text.split(' ')
    new_chunks = []
    chunk_start = 0
    i = 0
    for word in words:
        dbentity_name = word
        if dbentity_name.endswith('.') or dbentity_name.endswith(',') or dbentity_name.endswith('?') or dbentity_name.endswith('-'):
            dbentity_name = dbentity_name[:-1]
        if dbentity_name.endswith(')'):
            dbentity_name = dbentity_name[:-1]
        if dbentity_name.startswith('('):
            dbentity_name = dbentity_name[1:]

        dbentity = get_dbentity_by_name(dbentity_name.upper(), to_ignore, nex_session)

        if dbentity is not None:
            new_chunks.append(text[chunk_start: i])
            chunk_start = i + len(word) + 1

            new_chunk = "<a href='" + dbentity.link + "'>" + dbentity_name + "</a>"
            if word[-2] == ')':
                new_chunk = new_chunk + word[-2]
            if word.endswith('.') or word.endswith(',') or word.endswith('?') or word.endswith('-') or word.endswith(')'):
                new_chunk = new_chunk + word[-1]
            if word.startswith('('):
                new_chunk = word[0] + new_chunk
            new_chunks.append(new_chunk)
        i = i + len(word) + 1
    new_chunks.append(text[chunk_start: i])
    try:
        return ' '.join(new_chunks)
    except:
        print text
        return text


sgdid_to_reference_id = None

def get_sgdid_to_reference_id(sgdid, nex_session=None):
    from src.sgd.model.nex.reference import Reference
    global sgdid_to_reference_id
    if sgdid_to_reference_id is None:
        if nex_session is None:
            from src.sgd.model import nex
            from src.sgd.convert import config
            nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
            nex_session = nex_session_maker()
        sgdid_to_reference_id = {}
        for ref in nex_session.query(Reference).all():
            sgdid_to_reference_id[ref.sgdid] = ref.id
    return None if sgdid not in sgdid_to_reference_id else sgdid_to_reference_id[sgdid]

relation_to_ro_id = None

def get_relation_to_ro_id(relation_type, nex_session=None):
    from src.sgd.model.nex.ro import Ro
    global relation_to_ro_id
    if relation_to_ro_id is None:
        if nex_session is None:
            from src.sgd.model import nex
            from src.sgd.convert import config
            nex_session_maker = prepare_schema_connection(nex, config.NEX_DBTYPE, config.NEX_HOST, config.NEX_DBNAME, config.NEX_SCHEMA, config.NEX_DBUSER, config.NEX_DBPASS)
            nex_session = nex_session_maker()
        relation_to_ro_id = {}
        for relation in nex_session.query(Ro).all():
            relation_to_ro_id[relation.display_name] = relation.id
    return None if relation_type not in relation_to_ro_id else relation_to_ro_id[relation_type]

word_to_strain_id = None

def get_word_to_strain_id(word, nex_session):
    from src.sgd.model.nex.misc import Strain

    global word_to_strain_id
    if word_to_strain_id is None:
        word_to_strain_id = {}
        for strain in nex_session.query(Strain).all():
            if strain.link is not None:
                word_to_strain_id[strain.display_name.lower()] = strain.id

    word = word.lower()
    return None if word not in word_to_strain_id else word_to_strain_id[word]

def get_strain_by_name(strain_name, to_ignore, nex_session):
    from src.sgd.model.nex.misc import Strain
    if strain_name not in to_ignore:
        try:
            int(strain_name)
        except ValueError:
            strain_id = get_word_to_strain_id(strain_name, nex_session)
            return None if strain_id is None else nex_session.query(Strain).filter_by(id=strain_id).first()
    return None

def link_strain_names(text, to_ignore, nex_session):
    words = text.split(' ')
    new_chunks = []
    chunk_start = 0
    i = 0
    for word in words:
        strain_name = word
        if strain_name.endswith('.') or strain_name.endswith(',') or strain_name.endswith('?') or strain_name.endswith('-'):
            strain_name = strain_name[:-1]
        if strain_name.endswith(')'):
            strain_name = strain_name[:-1]
        if strain_name.startswith('('):
            strain_name = strain_name[1:]


        strain = get_strain_by_name(strain_name.upper(), to_ignore, nex_session)

        if strain is not None:
            new_chunks.append(text[chunk_start: i])
            chunk_start = i + len(word) + 1

            new_chunk = "<a href='" + strain.link + "'>" + strain_name + "</a>"
            if word[-2] == ')':
                new_chunk = new_chunk + word[-2]
            if word.endswith('.') or word.endswith(',') or word.endswith('?') or word.endswith('-') or word.endswith(')'):
                new_chunk = new_chunk + word[-1]
            if word.startswith('('):
                new_chunk = word[0] + new_chunk
            new_chunks.append(new_chunk)
        i = i + len(word) + 1
    new_chunks.append(text[chunk_start: i])
    try:
        return ' '.join(new_chunks)
    except:
        print text
        return text
