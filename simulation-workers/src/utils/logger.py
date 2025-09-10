"""
Configuration du logging pour les workers de simulation.
"""
import logging
import sys
from typing import Optional


def setup_logging(worker_name: str, log_level: str = 'INFO') -> logging.Logger:
    """Configure le logging pour un worker."""
    
    # Créer le logger
    logger = logging.getLogger(worker_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Créer le formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour les fichiers (optionnel)
    try:
        file_handler = logging.FileHandler(f'logs/{worker_name}.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # Ignorer si on ne peut pas créer le fichier de log
        pass
    
    return logger
