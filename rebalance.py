from decorators import execution_with_attempts
from binance import Client
import settings
import sys


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


def main():
    client = Client(settings.API_KEY, settings.API_SECRET)
    compiled_data = {}
    total_balance = 0.0
    for crypto, proportion in settings.portfolio_setting.items():
        balance = float(client.get_asset_balance(asset=crypto)['free'])  #  + float(client.get_asset_balance(asset=crypto)['locked'])
        avg_price = float(client.get_avg_price(symbol=f'{crypto}USDT')['price'])
        total_balance += (balance * avg_price)
        compiled_data[crypto] = {
            'balance': balance,
            'avg_price': avg_price,
            'usdt': balance * avg_price,
            'min_quantity': float(client.get_symbol_info(f'{crypto}USDT')['filters'][2]['minQty'])
        }

    print(f'TOTAL BALANCE: ${total_balance}')

    rebalance = {}
    for crypto, proportion in settings.portfolio_setting.items():
        wanted_balance = (settings.portfolio_setting[crypto] / 100) * total_balance
        current_usdt = compiled_data[crypto]['usdt']
        diff = current_usdt - wanted_balance
        if diff < 0:
            print(f'For crypto {crypto} - Wanted {round(wanted_balance, 2)} - Current {round(current_usdt, 2)} - BUY ${abs(round(diff, 2))}')
        else:
            print(f'For crypto {crypto} - Wanted {round(wanted_balance, 2)} - Current {round(current_usdt, 2)} - SELL ${abs(round(diff, 2))}')
        rebalance[crypto] = {
            'wanted_usdt': wanted_balance,
            'current_usdt': compiled_data[crypto]['usdt'],
            'diff': diff
        }

    print(f'Proceed with rebalance?')
    response = input('(y/n)').lower().strip()
    if response != 'y':
        sys.exit(0)

    real_amount_sold = 0.0
    required_amount_sold = 0.0

    # first sell operations
    for crypto, data in rebalance.items():
        diff = data['diff']
        if diff < 0:
            continue
        minimum = compiled_data[crypto]['min_quantity']
        quantity = abs(diff) - 5.0
        if quantity < minimum:
            continue
        quantity = '{:.8f}'.format(quantity)
        try:
            print(f'Selling USDT {quantity} of {crypto}')
            required_amount_sold += abs(diff) - 5.0

            # TODO uncomment this
            # place_sell_order(client, crypto, quantity)

            real_amount_sold += abs(diff) - 5.0
        except Exception as e:
            print(f'Warning, error selling {crypto}: {e}')
            continue

    if real_amount_sold == 0.0:
        print(f'Nothing sold. Exiting')
        sys.exit(0)

    amount_sold_factor = real_amount_sold / required_amount_sold

    # second buy operations
    for crypto, data in rebalance.items():
        diff = data['diff']
        if diff > 0:
            continue
        minimum = compiled_data[crypto]['min_quantity']
        for n in range(0, 50, 5):
            quantity = (abs(diff) - n) * amount_sold_factor
            if quantity < minimum:
                continue
            quantity = '{:.8f}'.format(quantity)
            try:
                print(f'Buying USDT {quantity} of {crypto}')

                # TODO uncomment this
                # place_buy_order(client, crypto, quantity)

                break
            except Exception as e:
                print(f'Warning, error buying {crypto}: {e}')
                continue


if __name__ == '__main__':
    main()
