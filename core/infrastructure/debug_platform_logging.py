import logging

from core.domain.interfaces import AbstractDebugPlatform


class LoggingDebugPlatform(AbstractDebugPlatform):
    def __init__(self):
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger()

    def register_exception(self, exception):
        self.logger.exception(exception)

    def register_message(self, message: str):
        self.logger.info(message)
