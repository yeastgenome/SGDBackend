'''
Created on Oct 11, 2013

@author: kpaskov
'''
from abc import abstractmethod, ABCMeta

class ConverterInterface:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def convert_daily(self):
        return None
    
    @abstractmethod
    def convert_monthly(self):
        return None
    
    @abstractmethod
    def convert_updated_flatfiles(self):
        return None
    
    @abstractmethod
    def convert_all(self):
        return None
    
   
    