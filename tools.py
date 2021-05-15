from decorators import execution_with_attempts


@execution_with_attempts(attempts=3, wait_seconds=5)
def place_buy_order(client, crypto, quantity):
    client.order_market_buy(
        symbol=f'{crypto}USDT',
        quoteOrderQty=quantity  # in usdt
    )


@execution_with_attempts(attempts=3, wait_seconds=5)
def place_sell_order(client, crypto, quantity):
    client.order_market_sell(
        symbol=f'{crypto}USDT',
        quoteOrderQty=quantity  # in usdt
    )