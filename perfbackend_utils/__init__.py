
from model_perf_schema.data import data_classes
from mpmath import ceil
from datetime import datetime
import logging

def set_up_logging(label):
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.INFO)
    log = logging.getLogger(label)
    
    hdlr = logging.FileHandler('perfbackend_logs/' + label + '.' + str(datetime.now().date()) + '.txt')
    formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr) 
    log.setLevel(logging.INFO)
    return log