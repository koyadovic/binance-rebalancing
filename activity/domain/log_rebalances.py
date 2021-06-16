from activity.domain.interfaces import AbstractActivityStorage
from shared.domain.dependencies import dependency_dispatcher
from shared.domain.event_dispatcher import event_dispatcher


@event_dispatcher.listens_on('crypto-asset-balance', uid_name='activity-crypto-asset-balance')
def _log_crypto_asset_balance(now=None, crypto_asset=None, balance=None):
    storage: AbstractActivityStorage = dependency_dispatcher.request_implementation(AbstractActivityStorage)
    print(f'[{now}] crypto-asset-balance {crypto_asset} {balance}')


@event_dispatcher.listens_on('total-balance', uid_name='activity-total-balance')
def _log_total_balance(now=None, fiat_asset=None, total_balance=None):
    storage: AbstractActivityStorage = dependency_dispatcher.request_implementation(AbstractActivityStorage)
    print(f'[{now}] total-balance {total_balance}')
