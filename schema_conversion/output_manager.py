'''
Created on Mar 8, 2013

@author: kpaskov
'''

class OutputCreator():
    num_added = 0
    num_changed = 0
    def added(self, message):
        self.num_added = self.num_added+1
        #if self.num_added%1000==0:
        #    print str(self.num_added) + ' ' + message + 's added.'
    
    def changed(self, message):
        self.num_changed = self.num_changed+1
        #if self.num_changed%1000==0:
        #    print str(self.num_changed) + ' ' + message + 's changed.'
    
    def finished(self, message):
        print 'In total ' + str(self.num_added) + ' ' + message + 's added.'
        print 'In total ' + str(self.num_changed) + ' ' + message + 's changed.'
        self.num_added = 0
        self.num_changed = 0
        
    def cached(self, message):
        print 'Cache finished for ' + message + '.'
