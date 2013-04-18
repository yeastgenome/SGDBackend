from numbers import Number
from sqlalchemy.types import Float
from utils.utils import float_approx_equal
import model_old_schema


    
def check_value(new_obj, old_obj, field_name):
    new_obj_value = getattr(new_obj, field_name)
    old_obj_value = getattr(old_obj, field_name)

    if isinstance(new_obj_value, (int, long, float, complex)) and isinstance(old_obj_value, (int, long, float, complex)):
        if not float_approx_equal(new_obj_value, old_obj_value):
            setattr(old_obj, field_name, new_obj_value)
            return False
    elif new_obj_value != old_obj_value:
        #print field_name
        #print new_obj_value
        #print old_obj_value
        setattr(old_obj, field_name, new_obj_value)
        return False
    return True

def check_values(new_obj, old_obj, field_names, output_creator, key):
    for field_name in field_names:
        if not check_value(new_obj, old_obj, field_name):
            output_creator.changed(key, field_name)

def cache(cls, mapping, key_maker, session, output_creator):
    new_entries = dict([(key_maker(x), x) for x in session.query(cls).all()])
    mapping.update(new_entries)
    output_creator.cached()
    
def add_or_check(new_obj, mapping, key, values_to_check, session, output_creator):
    if key in mapping:
        current_obj = mapping[key]
        check_values(new_obj, current_obj, values_to_check, output_creator, key)
        return False
    else:
        session.add(new_obj)
        mapping[key] = new_obj
        output_creator.added()
        return True
    
def create_or_update(old_objs, mapping, create, key_maker, values_to_check, session, output_creator):
    for old_obj in old_objs:
        new_obj = create(old_obj)
        if new_obj is not None:
            add_or_check(new_obj, mapping, key_maker, values_to_check, session, output_creator)
    output_creator.finished()
    
def create_or_update_and_remove(old_objs, mapping, create, key_maker, values_to_check, session, output_creator):
    to_be_removed = set(mapping.keys())
    for old_obj in old_objs:
        new_obj = create(old_obj)
        if new_obj is not None:
            key = key_maker(new_obj)
            add_or_check(new_obj, mapping, key, values_to_check, session, output_creator)
            
            if key in to_be_removed:
                to_be_removed.remove(key)
        
        output_creator.obj_completed()
    
    for r_id in to_be_removed:
        session.delete(mapping[r_id])
        output_creator.removed()
    output_creator.finished()
    
    
    