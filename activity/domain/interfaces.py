from activity.domain.entities import CryptoAssetBalance, TotalBalance


class AbstractActivityStorage:
    def save_crypto_asset_balance(self, crypto_asset_balance: CryptoAssetBalance):
        # if crypto_asset_balance.id is None, set it!
        raise NotImplementedError

    def save_total_balance(self, total_balance: TotalBalance):
        # if total_balance.id is None, set it!
        raise NotImplementedError
