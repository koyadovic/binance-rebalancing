from datetime import datetime


class Operation:
    pair: str
    type: str
    quote_amount: float
    base_currency: str
    quote_currency: str

    __slots__ = ('pair', 'type', 'quote_amount', 'base_currency', 'quote_currency')

    TYPE_BUY = 'BUY'
    TYPE_SELL = 'SELL'
    TYPES = [TYPE_SELL, TYPE_BUY]

    def __init__(self, pair=None, type=None, quote_amount=None):
        self.pair = pair.strip().upper()
        self.type = type
        self.quote_amount = quote_amount
        self._self_validation()
        self.base_currency = self.pair.split('/')[0]
        self.quote_currency = self.pair.split('/')[1]

    def _self_validation(self):
        if '/' not in str(self.pair):
            raise ValueError(f'Invalid pair format. Must be provided as \"BASE/COUNTER\". For example: \"BTC/BUSD\"')
        if self.type not in Operation.TYPES:
            raise ValueError(f'Invalid operation type. Accepted ones are: {", ".join(Operation.TYPES)}')
        if self.quote_amount is None or self.quote_amount < 0:
            raise ValueError(f'Invalid operation amount. Only positive values are allowed')

    def __str__(self):
        return f'{self.type} {self.pair} {self.quote_amount}'

    def __repr__(self):
        return self.__str__()

    def clone(self):
        return Operation(pair=self.pair, type=self.type, quote_amount=self.quote_amount)


class Candle:
    instant: datetime
    pair: str
    period: str

    open: float
    close: float
    high: float
    low: float

    volume: float

    PERIOD_HOUR = '1h'

    __slots__ = ('instant', 'pair', 'period', 'open', 'close', 'high', 'low', 'volume')

    def __init__(self, instant=None, pair=None, period=None, o=None, c=None, h=None, l=None, volume=None):
        self.instant = instant
        self.pair = pair
        self.open = o
        self.close = c
        self.high = h
        self.low = l
        self.period = period
        self.volume = volume

    def __str__(self):
        return f'[{self.instant}] {self.pair} O:{self.open} H:{self.high} L:{self.low} C:{self.close} VOL: {self.volume}'

    def __repr__(self):
        return self.__str__()

    def compute_profit(self):
        return ((self.close - self.open) / self.open) * 100.
