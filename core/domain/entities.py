class Operation:
    pair: str
    type: str
    counter_amount: float

    TYPE_BUY = 'BUY'
    TYPE_SELL = 'SELL'
    TYPES = [TYPE_SELL, TYPE_BUY]

    def __init__(self, pair=None, type=None, counter_amount=None):
        self.pair = pair.strip().upper()
        self.type = type
        self.counter_amount = counter_amount
        self._self_validation()

    @property
    def base_currency(self):
        return self.pair.split('/')[0]

    @property
    def counter_currency(self):
        return self.pair.split('/')[1]

    def _self_validation(self):
        if '/' not in str(self.pair):
            raise ValueError(f'Invalid pair format. Must be provided as \"BASE/COUNTER\". For example: \"BTC/BUSD\"')
        if self.type not in Operation.TYPES:
            raise ValueError(f'Invalid operation type. Accepted ones are: {", ".join(Operation.TYPES)}')
        if self.counter_amount is None or self.counter_amount < 0:
            raise ValueError(f'Invalid operation amount. Only positive values are allowed')

    def __str__(self):
        return f'{self.type} {self.counter_currency}{self.counter_amount} of {self.base_currency}'

    def __repr__(self):
        return self.__str__()
