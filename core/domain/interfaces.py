from typing import List

from core.domain.entities import Operation


class AbstractExchange:
    def get_asset_balance(self, asset: str) -> float:
        # if asset is BUSD, must return the amount of BUSD we have
        # if asset is BTC, must return the amount of BTC we have
        # and so on
        raise NotImplementedError

    def get_asset_price(self, base_asset: str, quote_asset: str, instant=None) -> float:
        # if asset is BTC and fiat_asset is USDT, must return the BTC price expressed as USDT
        raise NotImplementedError

    def place_buy_order(self, base_asset: str, quote_asset: str, quote_amount: float, **kwargs):
        raise NotImplementedError

    def place_sell_order(self, base_asset: str, quote_asset: str, quote_amount: float, **kwargs):
        raise NotImplementedError

    def compute_fees(self, operations: List[Operation], fiat_asset: str, **kwargs) -> float:
        raise NotImplementedError

    def get_exchange_valid_operations(self, operations: List[Operation]) -> List[Operation]:
        raise NotImplementedError

    def execute_operations(self, operations: List[Operation], **kwargs):
        raise NotImplementedError


class AbstractUserInterface:
    def show_rebalance_summary(self, summary: list, total_balance: str):
        raise NotImplementedError

    def request_confirmation(self, text: str) -> bool:
        raise NotImplementedError

    def show_message(self, text: str):
        raise NotImplementedError
