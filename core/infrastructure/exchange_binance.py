from typing import List

import requests

from core.domain.entities import Operation
from core.domain.interfaces import AbstractExchange
from binance import Client

from shared.domain.decorators import execution_with_attempts


class BinanceExchange(AbstractExchange):
    def __init__(self, api_key=None, api_secret=None):
        self._api_key = api_key
        self._api_secret = api_secret
        self._client = None
        self._exchange_info = None

    @property
    def client(self):
        # lazy client instantiation
        if self._client is None:
            self._client = Client(self._api_key, self._api_secret)
        return self._client

    @execution_with_attempts(attempts=3, wait_seconds=5)
    def get_asset_balance(self, asset: str) -> float:
        return float(self.client.get_asset_balance(asset=asset)['free'])

    @execution_with_attempts(attempts=3, wait_seconds=5)
    def get_asset_price(self, base_asset: str, quote_asset: str, **kwargs) -> float:
        return float(self.client.get_avg_price(symbol=f'{base_asset}{quote_asset}')['price'])

    @execution_with_attempts(attempts=3, wait_seconds=5)
    def place_buy_order(self, base_asset: str, quote_asset: str, quote_amount: float, **kwargs):
        quote_amount = '{:.8f}'.format(quote_amount)
        self.client.order_market_buy(
            symbol=f'{base_asset}{quote_asset}',
            quoteOrderQty=quote_amount
        )

    @execution_with_attempts(attempts=3, wait_seconds=5)
    def place_sell_order(self, base_asset: str, quote_asset: str, quote_amount: float, **kwargs):
        quote_amount = '{:.8f}'.format(quote_amount)
        self.client.order_market_sell(
            symbol=f'{base_asset}{quote_asset}',
            quoteOrderQty=quote_amount
        )

    def compute_fees(self, operations: List[Operation], fiat_asset: str, **kwargs) -> float:
        total_fees = 0.0
        for operation in operations:
            if operation.counter_currency == fiat_asset:
                total_fees += operation.counter_amount * (0.1 / 100.0)
            else:
                counter_fiat_price = self.get_asset_price(operation.counter_currency, fiat_asset, **kwargs)
                total_fees += (operation.counter_amount / counter_fiat_price) * (0.1 / 100.0)
        return total_fees

    def fix_operations_for_the_exchange(self, operations: List[Operation]) -> List[Operation]:
        # TODO
        return operations

    def execute_operations(self, operations: List[Operation]):
        # TODO
        pass

    @execution_with_attempts(attempts=3, wait_seconds=5)
    def _get_exchange_info(self):
        if self._exchange_info is None:
            response = requests.get('https://api.binance.com/api/v1/exchangeInfo')
            self._exchange_info = {symbol_data['symbol']: symbol_data for symbol_data in response.json()['symbols']}
        return self._exchange_info

    @classmethod
    def _fix_amount_by_step_size(cls, amount, step_size):
        # if step_size is 5, 99 will be converted to 95.0, which is the more conservative result.

        # If 99 with step_size of 5 need to be converted to 100,
        # amount // step_size could be changed to round(amount / step_size) before multiplying it by step_size again

        # the round(amount, 8) is to fix Python problems when amount // step_size * step_size
        # results in something like 99.0000000000000001.
        # round(99.0000000000000001, 8) results in 99.0 which is the right result
        # round(99.2200000000000001, 8) results in 99.22 which is the right result again
        return round(amount // step_size * step_size, 8)
