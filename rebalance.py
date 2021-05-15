from texttable import Texttable
from binance import Client
import settings
import sys

from decorators import execution_with_attempts
from tools import place_buy_order, place_sell_order


@execution_with_attempts(attempts=3, wait_seconds=5)
def get_compiled_balances(client):
    compiled_data = {}
    current_fiat_balance = float(client.get_asset_balance(asset=settings.fiat_asset)['free'])
    total_balance = current_fiat_balance
    for crypto, proportion in settings.portfolio_setting.items():
        # + float(client.get_asset_balance(asset=crypto)['locked'])
        balance = float(client.get_asset_balance(asset=crypto)['free'])
        avg_price = float(client.get_avg_price(symbol=f'{crypto}{settings.fiat_asset}')['price'])
        total_balance += (balance * avg_price)
        compiled_data[crypto] = {
            'balance': balance,
            'avg_price': avg_price,
            'fiat': balance * avg_price,
        }
    return compiled_data, current_fiat_balance, total_balance


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

    compiled_data, current_fiat_balance, total_balance = get_compiled_balances(client)

    do_something = False

    rebalance = {}
    for crypto, proportion in settings.portfolio_setting.items():
        wanted_balance = (settings.portfolio_setting[crypto] / 100) * total_balance
        current_fiat = compiled_data[crypto]['fiat']
        diff = current_fiat - wanted_balance

        current_percentage = round((current_fiat / total_balance) * 100, 2)
        target_percentage = round(settings.portfolio_setting[crypto], 2)

        row = [
            crypto,
            f'{settings.fiat_asset} {round(wanted_balance, 2)}',
            f'{target_percentage}%',
            f'{settings.fiat_asset} {round(current_fiat, 2)}',
            f'{current_percentage}%',
        ]

        if abs(diff) < 10.0:
            row.append(f'NOTHING')
        else:
            do_something = True
            if diff < 0:
                row.append(f'BUY {settings.fiat_asset} {abs(round(diff, 2))}')
            else:
                row.append(f'SELL {settings.fiat_asset} {abs(round(diff, 2))}')

        table_rows.append(row)
        rebalance[crypto] = {
            'wanted_fiat': wanted_balance,
            'current_fiat': compiled_data[crypto]['fiat'],
            'diff': diff
        }

    # Printing summary and asking for rebalancing
    table.add_rows(table_rows)
    print(table.draw() + '\n')
    print(f'TOTAL BALANCE: {settings.fiat_asset} {round(total_balance, 2)}')

    if not do_something:
        sys.exit(0)

    if len(sys.argv) == 1:
        print(f'Proceed with rebalance?')
        response = input('(y/n) ').lower().strip()
        if response != 'y':
            sys.exit(0)
    else:
        if sys.argv[1] not in ['--yes', '-y']:
            sys.exit(0)

    real_amount_sold = current_fiat_balance
    required_amount_sold = current_fiat_balance

    # first sell operations
    for crypto, data in rebalance.items():
        diff = data['diff']
        if diff < 0:
            continue
        quantity = abs(diff)
        if quantity < 10.0:
            continue
        quantity = '{:.8f}'.format(quantity)
        try:
            print(f'> Selling {settings.fiat_asset} {quantity} of {crypto}')
            required_amount_sold += abs(diff)
            place_sell_order(client, crypto, quantity)
            real_amount_sold += abs(diff)
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
            if quantity > real_amount_sold:
                quantity = real_amount_sold
            quantity = '{:.8f}'.format(quantity)
            try:
                print(f'> Buying {settings.fiat_asset} {quantity} of {crypto}')

                place_buy_order(client, crypto, quantity)
                break
            except Exception as e:
                print(f'! Warning, error buying {crypto}: {e}')
                continue


if __name__ == '__main__':
    main()
