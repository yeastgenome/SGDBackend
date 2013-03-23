import model_old_schema


    
def check_value(new_obj, old_obj, field_name):
    new_obj_value = getattr(new_obj, field_name)
    old_obj_value = getattr(old_obj, field_name)
    #print new_obj_value
    #print old_obj_value
    if new_obj_value != old_obj_value:
        #print field_name
        #print new_obj_value
        #print old_obj_value
        setattr(old_obj, field_name, new_obj_value)
        #print getattr(old_obj, field_name)
        return False
    return True

def check_values(new_obj, old_obj, field_names):
    match = True
    for field_name in field_names:
        match = check_value(new_obj, old_obj, field_name) and match
    return match

def cache(cls, mapping, key_maker, session, output_creator, output_message):
    new_entries = dict([(key_maker(x), x) for x in session.query(cls).all()])
    mapping.update(new_entries)
    output_creator.cached(output_message)
    
def add_or_check(new_obj, mapping, key_maker, values_to_check, session, output_creator, output_message, other_checks=None):
    key = key_maker(new_obj)
    if key in mapping:
        current_obj = mapping[key]
        match = check_values(new_obj, current_obj, values_to_check)
        if other_checks is not None:
            for check in other_checks:
                match = check(new_obj, current_obj) and match
                
        if not match:
            output_creator.changed(output_message)
    else:
        session.add(new_obj)
        mapping[key] = new_obj
        output_creator.added(output_message)
        
def create_or_update(old_objs, mapping, create, key_maker, values_to_check, session, output_creator, output_message, other_checks=None):
    for old_obj in old_objs:
        new_obj = create(old_obj)
        if new_obj is not None:
            add_or_check(new_obj, mapping, key_maker, values_to_check, session, output_creator, output_message, other_checks)
    output_creator.finished(output_message)
    
    
    