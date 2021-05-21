from binance import Client
import settings
from tools import place_fiat_sell_order


def main():
    client = Client(settings.API_KEY, settings.API_SECRET)
    for crypto, _ in settings.portfolio_setting.items():
        quantity = float(client.get_asset_balance(asset=crypto)['free'])
        avg_price = float(client.get_avg_price(symbol=f'{crypto}{settings.fiat_asset}')['price'])
        fiat_quantity = round(quantity * avg_price, 2)
        fiat_quantity -= 2.0
        if fiat_quantity < 10.0:
            continue
        fiat_quantity = '{:.8f}'.format(fiat_quantity)
        try:
            print(f'> Selling {crypto} {quantity} ~ {settings.fiat_asset} {fiat_quantity}')
            place_fiat_sell_order(client, crypto, fiat_quantity)
        except Exception as e:
            print(f'! Warning, error selling {crypto}: {e}')
            continue


if __name__ == '__main__':
    main()
