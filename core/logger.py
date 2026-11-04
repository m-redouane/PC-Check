import logging
import os

# Configuration du dossier de logs
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE = os.path.join(LOG_DIR, "pc_check_debug.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()  # Affiche aussi dans la console du terminal
    ]
)

def get_logger(name):
    return logging.getLogger(name)