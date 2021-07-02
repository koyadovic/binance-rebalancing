import sentry_sdk
from sentry_sdk import capture_exception, capture_message

from core.domain.interfaces import AbstractDebugPlatform


class SentryDebugPlatform(AbstractDebugPlatform):
    def __init__(self, *args, sentry_dsn=None, **kwargs):
        super().__init__(*args, **kwargs)
        sentry_sdk.init(sentry_dsn, traces_sample_rate=1.0)

    def register_exception(self, exception):
        capture_exception(exception)

    def register_message(self, message: str):
        capture_message(message)
