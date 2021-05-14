from texttable import Texttable
from binance import Client
import settings
import sys

from tools import place_buy_order, place_sell_order


def main():
    table = Texttable()
    table.set_cols_align(["c", "c", "c", "c", "c", "c"])
    table_rows = [[
        'Symbol',
        'Wanted amount',
        'Wanted %',
        'Current amount',
        'Current %',
        'Action'
    ]]

    client = Client(settings.API_KEY, settings.API_SECRET)

    compiled_data = {}

    total_balance = float(client.get_asset_balance(asset='USDT')['free'])
    for crypto, proportion in settings.portfolio_setting.items():
        balance = float(client.get_asset_balance(asset=crypto)['free'])  # + float(client.get_asset_balance(asset=crypto)['locked'])
        avg_price = float(client.get_avg_price(symbol=f'{crypto}USDT')['price'])
        total_balance += (balance * avg_price)
        compiled_data[crypto] = {
            'balance': balance,
            'avg_price': avg_price,
            'usdt': balance * avg_price,
        }

    rebalance = {}
    for crypto, proportion in settings.portfolio_setting.items():
        wanted_balance = (settings.portfolio_setting[crypto] / 100) * total_balance
        current_usdt = compiled_data[crypto]['usdt']
        diff = current_usdt - wanted_balance

        current_percentage = round((current_usdt / total_balance) * 100, 2)
        target_percentage = round(settings.portfolio_setting[crypto], 2)

        row = [
            crypto,
            f'${round(wanted_balance, 2)}',
            f'{target_percentage}%',
            f'${round(current_usdt, 2)}',
            f'{current_percentage}%',
        ]

        if diff < 0:
            row.append(f'BUY ${abs(round(diff, 2))}')
        else:
            row.append(f'SELL ${abs(round(diff, 2))}')

        table_rows.append(row)
        rebalance[crypto] = {
            'wanted_usdt': wanted_balance,
            'current_usdt': compiled_data[crypto]['usdt'],
            'diff': diff
        }

    # Printing summary and asking for rebalancing
    table.add_rows(table_rows)
    print(table.draw() + '\n')
    print(f'TOTAL BALANCE: ${round(total_balance, 2)}')
    print(f'Proceed with rebalance?')
    response = input('(y/n) ').lower().strip()
    if response != 'y':
        sys.exit(0)

    real_amount_sold = 0.0
    required_amount_sold = 0.0

    # first sell operations
    for crypto, data in rebalance.items():
        diff = data['diff']
        if diff < 0:
            continue
        quantity = abs(diff) - 5.0
        if quantity < 10.0:
            continue
        quantity = '{:.8f}'.format(quantity)
        try:
            print(f'> Selling USDT {quantity} of {crypto}')
            required_amount_sold += abs(diff) - 5.0
            # place_sell_order(client, crypto, quantity)
            real_amount_sold += abs(diff) - 5.0
        except Exception as e:
            print(f'! Warning, error selling {crypto}: {e}')
            continue

    if real_amount_sold == 0.0:
        print(f'! Nothing sold. Exiting')
        sys.exit(0)

    amount_sold_factor = real_amount_sold / required_amount_sold

    # second buy operations
    for crypto, data in rebalance.items():
        diff = data['diff']
        if diff > 0:
            continue
        for n in range(0, 50, 5):
            quantity = (abs(diff) - n) * amount_sold_factor
            if quantity < 10.:
                break
            quantity = '{:.8f}'.format(quantity)
            try:
                print(f'> Buying USDT {quantity} of {crypto}')

                # place_buy_order(client, crypto, quantity)
                break
            except Exception as e:
                print(f'! Warning, error buying {crypto}: {e}')
                continue


if __name__ == '__main__':
    main()
