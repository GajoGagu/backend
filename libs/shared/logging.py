import logging, os, sys
def setup_json_logger(name: str = "app"):
    handler = logging.StreamHandler(sys.stdout)
    fmt = '{"level":"%(levelname)s","ts":"%(asctime)s","logger":"%(name)s","msg":"%(message)s"}'
    handler.setFormatter(logging.Formatter(fmt))
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    logger.handlers = [handler]
    return logger
