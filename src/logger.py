import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

def setup_logger(name, log_file):


    output_dir = 'Logs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    

    subdirectories = ['register', 'login', 'create']
    for subdir in subdirectories:
        subdir_path = os.path.join(output_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)
        
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(filename=log_file.format(date=datetime.datetime.now().strftime('%d-%m-%Y')), when='midnight', interval=1, encoding='utf-8', backupCount=0)
    handler.setFormatter(log_formatter)

    logger.addHandler(handler)

    return logger
