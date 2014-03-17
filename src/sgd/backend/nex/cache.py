from string import lower
from math import ceil

from sqlalchemy.sql import func

from obj_to_json import bioent_to_json, experiment_to_json, strain_to_json, \
    biocon_to_json, reference_to_json
from obj_to_json import bioitem_to_json, source_to_json, \
    chemical_to_json


__author__ = 'kpaskov'

id_to_bioent = {}
id_to_biocon = {}
id_to_bioitem = {}
id_to_experiment = {}
id_to_strain = {}
id_to_reference = {}
id_to_source = {}
id_to_chem = {}

word_to_bioent_id = {}
class_to_cache_info = {}

def cache_core():

    from src.sgd.model.nex.bioentity import Bioentity
    from src.sgd.model.nex.bioconcept import Bioconcept
    from src.sgd.model.nex.bioitem import Bioitem
    from src.sgd.model.nex.evelements import Experiment, Strain, Source
    from src.sgd.model.nex.reference import Reference
    from src.sgd.model.nex.chemical import Chemical

    class_to_cache_info[Bioconcept] = (id_to_biocon, biocon_to_json)
    class_to_cache_info[Bioentity] = (id_to_bioent, bioent_to_json)
    class_to_cache_info[Bioitem] = (id_to_bioitem, bioitem_to_json)
    class_to_cache_info[Source] = (id_to_source, source_to_json)
    class_to_cache_info[Experiment] = (id_to_experiment, experiment_to_json)
    class_to_cache_info[Strain] = (id_to_strain, strain_to_json)
    class_to_cache_info[Reference] = (id_to_reference, reference_to_json)
    class_to_cache_info[Chemical] = (id_to_chem, chemical_to_json)

    #get_all_objs(Bioentity)
    get_all_objs(Source)
    get_all_objs(Experiment)
    get_all_objs(Strain)

def get_obj(cls, obj_id):
    id_to_obj, obj_to_json = class_to_cache_info[cls]

    if obj_id in id_to_obj:
        return id_to_obj[obj_id]
    else:
        from src.sgd.backend.nex import DBSession
        obj = DBSession.query(cls).filter(cls.id == obj_id).first()
        if obj is not None:
            id_to_obj[obj_id] = obj_to_json(obj)
            return id_to_obj[obj_id]
    return None

def get_objs(cls, obj_ids):
    obj_ids = set(obj_ids)
    id_to_obj, obj_to_json = class_to_cache_info[cls]

    already_have = set(id_to_obj.keys()) & obj_ids
    still_need = obj_ids - already_have

    from src.sgd.backend.nex import DBSession
    if len(still_need) < 500:
        for obj in DBSession.query(cls).filter(cls.id.in_(still_need)).all():
            id_to_obj[obj.id] = obj_to_json(obj)
    else:
        num_chunks = int(ceil(1.0*len(still_need)/500))
        still_need = list(still_need)
        for i in range(0, num_chunks):
            for obj in DBSession.query(cls).filter(cls.id.in_(still_need[i*500:(i+1)*500])).all():
                id_to_obj[obj.id] = obj_to_json(obj)

    return dict([(x, get_obj(cls, x)) for x in obj_ids])

def get_all_objs(cls):
    id_to_obj, obj_to_json = class_to_cache_info[cls]

    from src.sgd.backend.nex import DBSession
    if DBSession.query(cls).count() != len(id_to_obj):
        for obj in DBSession.query(cls).all():
            id_to_obj[obj.id] = obj_to_json(obj)

    return id_to_obj

def get_word_to_bioent_id(word):
    from src.sgd.backend.nex import DBSession
    from src.sgd.model.nex.bioentity import Bioentity

    word = lower(word)

    if word in word_to_bioent_id:
        return word_to_bioent_id[word]

    bioentities = DBSession.query(Bioentity).filter(Bioentity.class_type == 'LOCUS').filter(func.lower(Bioentity.display_name) == word).all()
    bioentities.extend(DBSession.query(Bioentity).filter(Bioentity.class_type == 'LOCUS').filter(func.lower(Bioentity.display_name) == word).all())

    bioentities.extend(DBSession.query(Bioentity).filter(Bioentity.class_type == 'LOCUS').filter(func.lower(Bioentity.format_name) == word).all())
    bioentities.extend(DBSession.query(Bioentity).filter(Bioentity.class_type == 'LOCUS').filter(func.lower(Bioentity.format_name) == word).all())

    for bioentity in bioentities:
        word_to_bioent_id[lower(bioentity.display_name)] = bioentity.id
        word_to_bioent_id[lower(bioentity.display_name) + 'p'] = bioentity.id
        word_to_bioent_id[lower(bioentity.format_name)] = bioentity.id
        word_to_bioent_id[lower(bioentity.format_name) + 'p'] = bioentity.id

    return None if word not in word_to_bioent_id else word_to_bioent_id[word]

def get_words_to_bioent_id(words):
    from src.sgd.backend.nex import DBSession
    from src.sgd.model.nex.bioentity import Bioentity

    words = set([lower(x) for x in words])
    already_have = words & word_to_bioent_id.keys()

    still_need = words - already_have
    still_need_ending_in_p = [x[:-1] for x in still_need if x[-1] == 'p']

    bioentities = DBSession.query(Bioentity).filter(Bioentity.class_type == 'LOCUS').filter(func.lower(Bioentity.display_name).in_(still_need)).all()
    bioentities.extend(DBSession.query(Bioentity).filter(Bioentity.class_type == 'LOCUS').filter(func.lower(Bioentity.display_name).in_(still_need_ending_in_p)).all())

    bioentities.extend(DBSession.query(Bioentity).filter(Bioentity.class_type == 'LOCUS').filter(func.lower(Bioentity.format_name).in_(still_need)).all())
    bioentities.extend(DBSession.query(Bioentity).filter(Bioentity.class_type == 'LOCUS').filter(func.lower(Bioentity.format_name).in_(still_need_ending_in_p)).all())

    for bioentity in bioentities:
        word_to_bioent_id[lower(bioentity.display_name)] = bioentity.id
        word_to_bioent_id[lower(bioentity.display_name) + 'p'] = bioentity.id
        word_to_bioent_id[lower(bioentity.format_name)] = bioentity.id
        word_to_bioent_id[lower(bioentity.format_name) + 'p'] = bioentity.id

    no_ids = words - word_to_bioent_id.keys()
    for no_id in no_ids:
        word_to_bioent_id[no_id] = None

    return word_to_bioent_id
