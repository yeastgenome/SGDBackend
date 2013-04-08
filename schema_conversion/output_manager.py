'''
Created on Mar 8, 2013

@author: kpaskov
'''

class OutputCreator():
    num_added = 0
    changed_keys = set()
    fields_changed = {}
    num_removed = 0
    
    num_completed = 0
    
    def __init__(self, new_obj_type):
        self.new_obj_type = new_obj_type
        
    def added(self):
        self.num_added = self.num_added+1
        
    def removed(self):
        self.num_removed = self.num_removed+1
    
    def changed(self, key, field_name):
        self.changed_keys.add(key)
        if field_name in self.fields_changed:
            self.fields_changed[field_name] = self.fields_changed[field_name] + 1
        else:
            self.fields_changed[field_name] = 1
            
    def obj_completed(self):
        self.num_completed = self.num_completed + 1
        if self.num_completed%1000 == 0:
            print str(self.num_completed) + '/' + str(self.old_total) + ' ' + self.old_obj_type + ' conversions complete.'
            
    def pulled(self, old_obj_type, old_total):
        self.old_obj_type = old_obj_type
        self.old_total = old_total
        print 'All ' + self.old_obj_type + ' objects pulled.'
        
    
    def finished(self):
        print 'In total ' + str(self.num_added) + ' ' + self.new_obj_type + 's added.'
        print 'In total ' + str(len(self.changed_keys)) + ' ' + self.new_obj_type + 's changed.'
        for (field, num_changed) in self.fields_changed.iteritems():
            print '   ' + str(num_changed) + ' ' + field + 's changed.'
        print 'In total ' + str(self.num_removed) + ' ' + self.new_obj_type + 's removed.'
        
    def cached(self):
        print 'Cache finished for ' + self.new_obj_type + '.'
    
