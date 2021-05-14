from binance import Client
import settings
from tools import place_sell_order


def main():
    client = Client(settings.API_KEY, settings.API_SECRET)
    for crypto, _ in settings.portfolio_setting.items():
        balance = float(client.get_asset_balance(asset=crypto)['free'])
        avg_price = float(client.get_avg_price(symbol=f'{crypto}USDT')['price'])
        usdt = balance * avg_price

        for n in range(0, 50, 5):
            quantity = usdt - n
            if quantity < 10.0:
                continue
            quantity = '{:.8f}'.format(quantity)
            try:
                print(f'> Selling USDT {quantity} of {crypto}')
                # place_sell_order(client, crypto, quantity)
                break
            except Exception as e:
                print(f'! Warning, error selling {crypto}: {e}')
                continue


if __name__ == '__main__':
    main()
