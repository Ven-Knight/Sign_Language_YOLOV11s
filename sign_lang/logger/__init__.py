# ─────────────────────────────────────────────────────────────
# Logger Setup — Console Only, No Log Files
# ─────────────────────────────────────────────────────────────

import logging

# Singleton named logger
logger = logging.getLogger("sign_lang_logger")

# Prevent duplicate handlers
if not logger.handlers:
    # Console handler only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter       = logging.Formatter("[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set logger level
    logger.setLevel(logging.INFO)

# Export logger
__all__ = ["logger"]
