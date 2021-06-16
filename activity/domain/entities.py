class CryptoAssetBalance:
    def __init__(self, id=None, timestamp=None, asset=None, balance=None):
        self.id = id
        self.timestamp = timestamp
        self.asset = asset
        self.balance = balance

    def __str__(self):
        return f'[{self.timestamp}] {self.asset} {self.balance}'

    def __repr__(self):
        return self.__str__()


class TotalBalance:
    def __init__(self, id=None, timestamp=None, fiat_asset=None, total_balance=None):
        self.id = id
        self.timestamp = timestamp
        self.fiat_asset = fiat_asset
        self.total_balance = total_balance

    def __str__(self):
        return f'[{self.timestamp}] {self.fiat_asset} {self.total_balance}'

    def __repr__(self):
        return self.__str__()
