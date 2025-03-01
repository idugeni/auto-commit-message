import os
import logging
import colorlog
from config import Config

class CustomFormatter(colorlog.ColoredFormatter):
    """Custom formatter for consistent log level"""
    def format(self, record):
        return super().format(record)

class LoggerSetup:
    """Setup logging configuration"""
    @staticmethod
    def setup() -> logging.Logger:
        """Configure and return logger with colored output"""
        handler = colorlog.StreamHandler()
        handler.setFormatter(CustomFormatter(
            Config.LOG_FORMAT,
            datefmt=Config.LOG_DATE_FORMAT,
            log_colors=Config.LOG_COLORS
        ))

        logger = logging.getLogger('auto-commit-message')
        logger.setLevel(logging.DEBUG)
        logger.handlers = []  # Menghapus handler yang sudah ada
        logger.addHandler(handler)

        os.environ.update({
            "GRPC_VERBOSITY": "ERROR",
            "GLOG_minloglevel": "2",
            "GRPC_TRACE": ""
        })

        return logger
