"""Logger module containing the Isoplot logger initialization"""

import logging

#Setup base logger

logger = logging.getLogger("isoplot_log")
logger.setLevel(logging.DEBUG)