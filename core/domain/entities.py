class Operation:
    pair: str
    type: str
    amount: float

    TYPE_BUY = 'BUY'
    TYPE_SELL = 'SELL'

    def __init__(self, pair=None, type=None, amount=None):
        self.pair = pair
        self.type = type
        self.amount = amount

    def __str__(self):
        return f'{self.type} {self.amount} {self.pair}'

    def __repr__(self):
        return self.__str__()
