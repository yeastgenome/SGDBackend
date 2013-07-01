'''
Created on Mar 8, 2013

@author: kpaskov
'''

class OutputCreator():
    num_added = 0
    num_changed = 0
    fields_changed = {}
    num_removed = 0
    
    
    def added(self):
        self.num_added = self.num_added+1
        
    def removed(self):
        self.num_removed = self.num_removed+1
    
    def changed(self, key, field_name):
        self.num_changed = self.num_changed+1
        if field_name in self.fields_changed:
            self.fields_changed[field_name] = self.fields_changed[field_name] + 1
        else:
            self.fields_changed[field_name] = 1
            
    def finished(self):
        print 'In total ' + str(self.num_added) + ' added.'
        print 'In total ' + str(self.num_changed) + ' changed.'
        for (field, changed) in self.fields_changed.iteritems():
            print '   ' + str(changed) + ' ' + field + 's changed.'
        print 'In total ' + str(self.num_removed) + ' removed.'
        
        self.num_added = 0
        self.num_changed = 0
        self.fields_changed.clear()
        self.num_removed = 0
    
    def change_made(self):
        return self.num_added + self.num_changed + self.num_removed != 0