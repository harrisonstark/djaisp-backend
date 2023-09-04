import logging

def configure_logging():
    logging.basicConfig(filename='/app/log/djaisp-backend.log', level=logging.ERROR)