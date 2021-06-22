class AbstractExchange:
    def get_asset_balance(self, asset: str) -> float:
        # if asset is BUSD, must return the amount of BUSD we have
        # if asset is BTC, must return the amount of BTC we have
        # and so on
        raise NotImplementedError

    def get_asset_fiat_price(self, asset: str, fiat_asset: str, instant=None) -> float:
        # if asset is BTC and fiat_asset is USDT, must return the BTC price expressed as USDT
        raise NotImplementedError

    def place_fiat_buy_order(self, crypto: str, quantity: float, fiat_asset: str, **kwargs):
        raise NotImplementedError

    def place_fiat_sell_order(self, crypto: str, quantity: float, fiat_asset: str, **kwargs):
        raise NotImplementedError


class AbstractUserInterface:
    def show_rebalance_summary(self, summary: list, total_balance: str):
        raise NotImplementedError

    def request_confirmation(self, text: str) -> bool:
        raise NotImplementedError

    def show_message(self, text: str):
        raise NotImplementedError
