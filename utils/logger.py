import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with a specified name.
    
    :param name: Name of the logger.
    :return: Configured logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger
