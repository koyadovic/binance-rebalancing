from activity.domain.interfaces import AbstractActivityStorage
from activity.infrastructure.activity_storage_sqlite3 import SQLite3ActivityStorage
from shared.domain.dependencies import dependency_dispatcher

# this cannot be removed
from activity.domain import log_rebalances


def init_activity_module():
    dependency_dispatcher.register_implementation(
        AbstractActivityStorage,
        SQLite3ActivityStorage()
    )
