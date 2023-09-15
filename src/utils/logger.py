import logging
import os

def configure_logging():
    log_directory = '/app/log/'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    logging.basicConfig(filename='/app/log/djaisp-backend.log', level=logging.ERROR)
    
    # Create and return a logger object
    return logging.getLogger(__name__)