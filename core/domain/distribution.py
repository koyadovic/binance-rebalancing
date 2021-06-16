class Distribution:
    def __init__(self, crypto_assets):
        self.crypto_assets = crypto_assets

    def assign_percentage(self, crypto: str) -> float:  # must return 0.0 to 100.0
        raise NotImplementedError

    class Error(Exception):
        pass


class EqualDistribution(Distribution):
    def assign_percentage(self, crypto: str) -> float:
        return 100.0 / len(self.crypto_assets)


class CustomDistribution(Distribution):
    def __init__(self, crypto_assets, percentages=None):
        super().__init__(crypto_assets)
        self.percentages = percentages or dict()

    def assign_percentage(self, crypto: str) -> float:
        if crypto not in self.percentages:
            raise Distribution.Error(f'{crypto} does not exist into percentages parameter')
        if type(self.percentages[crypto]) not in [float, int]:
            raise Distribution.Error(f'invalid percentage provided for {crypto}')
        self.percentages[crypto] = float(self.percentages[crypto])
        try:
            assert 0 <= self.percentages[crypto] <= 100.0, f'invalid percentage provided for {crypto}'
        except AssertionError as e:
            raise Distribution.Error(str(e))
        return self.percentages[crypto]
