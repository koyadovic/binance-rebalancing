from core.domain.interfaces import AbstractExchange
from binance import Client

from shared.domain.decorators import execution_with_attempts


class BinanceExchange(AbstractExchange):
    def __init__(self, api_key=None, api_secret=None):
        self._api_key = api_key
        self._api_secret = api_secret
        self._client = None

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
    def get_asset_fiat_price(self, asset: str, fiat_asset: str) -> float:
        return float(self.client.get_avg_price(symbol=f'{asset}{fiat_asset}')['price'])

    @execution_with_attempts(attempts=3, wait_seconds=5)
    def place_fiat_buy_order(self, crypto: str, quantity: float, fiat_asset: str):
        quantity = '{:.8f}'.format(quantity)
        self.client.order_market_buy(
            symbol=f'{crypto}{fiat_asset}',
            quoteOrderQty=quantity
        )

    @execution_with_attempts(attempts=3, wait_seconds=5)
    def place_fiat_sell_order(self, crypto: str, quantity: float, fiat_asset: str):
        quantity = '{:.8f}'.format(quantity)
        self.client.order_market_sell(
            symbol=f'{crypto}{fiat_asset}',
            quoteOrderQty=quantity
        )
