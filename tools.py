import settings
from decorators import execution_with_attempts


@execution_with_attempts(attempts=3, wait_seconds=5)
def place_fiat_buy_order(client, crypto, quantity):
    client.order_market_buy(
        symbol=f'{crypto}{settings.fiat_asset}',
        quoteOrderQty=quantity
    )


@execution_with_attempts(attempts=3, wait_seconds=5)
def place_fiat_sell_order(client, crypto, quantity):
    client.order_market_sell(
        symbol=f'{crypto}{settings.fiat_asset}',
        quoteOrderQty=quantity
    )


@execution_with_attempts(attempts=3, wait_seconds=5)
def place_crypto_sell_order(client, crypto, quantity):
    client.order_market_sell(
        symbol=f'{crypto}{settings.fiat_asset}',
        quantity=quantity
    )
