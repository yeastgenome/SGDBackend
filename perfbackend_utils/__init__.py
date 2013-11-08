
from datetime import datetime
from model_perf_schema.data import data_classes
from mpmath import ceil
from perfbackend.config import log_directory
import logging

def set_up_logging(label):
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.INFO)
    log = logging.getLogger(label)
    
    if log_directory is not None:
        hdlr = logging.FileHandler(log_directory + '/' + label + '.' + str(datetime.now().date()) + '.txt')
        formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s')
        hdlr.setFormatter(formatter)
    else:
        hdlr = logging.NullHandler()
    log.addHandler(hdlr) 
    log.setLevel(logging.INFO)
    return log