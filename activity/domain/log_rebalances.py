from activity.domain.entities import CryptoAssetBalance, TotalBalance
from activity.domain.interfaces import AbstractActivityStorage
from shared.domain.dependencies import dependency_dispatcher
from shared.domain.event_dispatcher import event_dispatcher


@event_dispatcher.listens_on('crypto-asset-balance', uid_name='activity-crypto-asset-balance')
def _log_crypto_asset_balance(now=None, crypto_asset=None, balance=None):
    storage: AbstractActivityStorage = dependency_dispatcher.request_implementation(AbstractActivityStorage)
    asset_balance = CryptoAssetBalance(timestamp=now, asset=crypto_asset, balance=balance)
    storage.save_crypto_asset_balance(asset_balance)


@event_dispatcher.listens_on('total-balance', uid_name='activity-total-balance')
def _log_total_balance(now=None, fiat_asset=None, total_balance=None):
    storage: AbstractActivityStorage = dependency_dispatcher.request_implementation(AbstractActivityStorage)
    total_balance = TotalBalance(timestamp=now, fiat_asset=fiat_asset, total_balance=total_balance)
    storage.save_total_balance(total_balance)
