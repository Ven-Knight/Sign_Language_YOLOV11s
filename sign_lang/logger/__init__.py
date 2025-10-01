# ─────────────────────────────────────────────────────────────
# Logger Setup — Single File Per Run, Audit-Ready
# ─────────────────────────────────────────────────────────────

# import logging
# import os
# from datetime import datetime
# from from_root import from_root  # Resolves project root path

# # Create log directory under project root
# log_dir = os.path.join(from_root(), 'log')
# os.makedirs(log_dir, exist_ok=True)

# # Configure logging only once
# logger = logging.getLogger()
# if not logger.hasHandlers():
#     # Generate timestamped log filename
#     log_filename = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
#     log_file_path = os.path.join(log_dir, log_filename)

#     # File handler
#     file_handler = logging.FileHandler(log_file_path)
#     file_handler.setLevel(logging.INFO)
#     formatter = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)

#     # Optional: Console handler for debugging
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.INFO)
#     console_handler.setFormatter(formatter)
#     logger.addHandler(console_handler)

#     # Set root logger level
#     logger.setLevel(logging.INFO)

# ─────────────────────────────────────────────────────────────
# Logger Setup — Named Singleton, One File Per Run
# ─────────────────────────────────────────────────────────────

import logging
import os
from datetime import datetime
from from_root import from_root

# Create log directory
log_dir = os.path.join(from_root(), 'log')
os.makedirs(log_dir, exist_ok=True)

# Use a named logger to avoid root-level duplication
logger = logging.getLogger("sign_lang_logger")

# Prevent multiple handlers
if not logger.handlers:
    log_filename = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
    log_file_path = os.path.join(log_dir, log_filename)

    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set logger level
    logger.setLevel(logging.INFO)

# Export the singleton logger
__all__ = ["logger"]