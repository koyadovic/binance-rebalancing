import json
import os
from datetime import datetime, timedelta
from typing import List

from core.domain.entities import Operation
from core.domain.interfaces import AbstractExchange
from binance import Client
from shared.domain.decorators import execution_with_attempts


class BinanceSimulationExchange(AbstractExchange):

    def __init__(self, api_key=None, api_secret=None):
        self._api_key = api_key
        self._api_secret = api_secret
        self._client = None
        self._month_prices = {}

        self.balances = {}

    @property
    def client(self):
        # lazy client instantiation
        if self._client is None:
            self._client = Client(self._api_key, self._api_secret)
        return self._client

    def reset_balances(self, fiat_asset, fiat_balance):
        self.balances = {fiat_asset: fiat_balance}

    def get_asset_balance(self, asset: str) -> float:
        return self.balances.get(asset, 0.0)

    def get_asset_fiat_price(self, asset: str, fiat_asset: str, instant=None) -> float:
        discrete_instant = datetime(instant.year, instant.month, instant.day, instant.hour, 0, 0)
        dict_month_prices = self.get_month_prices(asset, fiat_asset, discrete_instant)
        for delta_h in range(0, 48):
            try:
                return dict_month_prices[discrete_instant - timedelta(hours=delta_h)]['open']
            except KeyError:
                pass
            try:
                return dict_month_prices[discrete_instant + timedelta(hours=delta_h)]['open']
            except KeyError:
                pass
        raise Exception(f'Cannot find price for {asset} at {discrete_instant}')

    def place_fiat_buy_order(self, crypto: str, quantity: float, fiat_asset: str, avg_price=None):
        crypto_balance = self.get_asset_balance(crypto)
        fiat_balance = self.get_asset_balance(fiat_asset)

        if fiat_balance < quantity:
            print('!!!!!!!!!!!!! NO SE PUEDE COMPRAR !!!!!!!!!!!!!')
            return

        fiat_balance -= quantity
        quantity *= 0.999  # binance fee
        crypto_balance += quantity / avg_price

        self.balances[fiat_asset] = fiat_balance
        self.balances[crypto] = crypto_balance

    def place_fiat_sell_order(self, crypto: str, quantity: float, fiat_asset: str, avg_price=None):
        crypto_balance = self.get_asset_balance(crypto)
        fiat_balance = self.get_asset_balance(fiat_asset)

        if crypto_balance < (quantity / avg_price):
            print('!!!!!!!!!!!!! NO SE PUEDE VENDER !!!!!!!!!!!!!')
            return

        crypto_balance -= quantity / avg_price
        quantity *= 0.999  # binance fee
        fiat_balance += quantity

        self.balances[fiat_asset] = fiat_balance
        self.balances[crypto] = crypto_balance

    @execution_with_attempts(attempts=3, wait_seconds=5)
    def get_month_prices(self, asset, fiat_asset, instant):
        name = f'{asset}{fiat_asset}_{instant.year}_{instant.month}'
        if f'{name}' in self._month_prices:
            return self._month_prices[name]

        filename = f'data/{name}.json'
        if not os.path.isfile(filename):
            start_date_str = instant.strftime('1 %b, %Y')
            try:
                end_date = datetime(instant.year, instant.month + 1, 1)
            except ValueError:
                end_date = datetime(instant.year + 1, 1, 1)
            end_date_str = end_date.strftime('1 %b, %Y')

            raw_data = self.client.get_historical_klines(
                f'{asset}{fiat_asset}', Client.KLINE_INTERVAL_1HOUR, start_date_str, end_date_str)

            data = [self.parse_data_item(item) for item in raw_data[:-1]]
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

        prices = [
            {
                'utc_datetime': datetime.utcfromtimestamp(item['timestamp'] / 1000),
                'open': item['open'],
                'high': item['high'],
                'low': item['low'],
                'close': item['close'],
                'volume': item['volume'],
            } for item in data
        ]
        if len(prices) == 0:
            raise Exception(f'There is no prices in {name}')

        dict_prices = {price['utc_datetime']: price for price in prices}
        self._month_prices[name] = dict_prices
        return dict_prices

    @classmethod
    def parse_data_item(cls, data_item):
        return {
            'timestamp': data_item[0],
            'open': float(data_item[1]),
            'high': float(data_item[2]),
            'low': float(data_item[3]),
            'close': float(data_item[4]),
            'volume': float(data_item[5]),
        }

    def compute_fees(self, operations: List[Operation], fiat_asset: str, **kwargs) -> float:
        total_fees = 0.0
        for operation in operations:
            if operation.counter_currency == fiat_asset:
                total_fees += operation.counter_amount * (0.1 / 100.0)
            else:
                counter_fiat_price = self.get_asset_fiat_price(operation.counter_currency, fiat_asset, **kwargs)
                total_fees += (operation.counter_amount / counter_fiat_price) * (0.1 / 100.0)
        return total_fees
