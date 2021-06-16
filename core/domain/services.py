from datetime import datetime

import pytz

from core.domain.interfaces import AbstractExchange, AbstractUserInterface
from shared.domain.dependencies import dependency_dispatcher
from shared.domain.event_dispatcher import event_dispatcher


def rebalance(crypto_assets: list = None, fiat_asset: str = None,
              fiat_decimals: str = None, exposure: float = None, with_confirmation=True, now=None):

    now = now or datetime.utcnow().replace(tzinfo=pytz.utc)

    # dependencies
    user_interface: AbstractUserInterface = dependency_dispatcher.request_implementation(AbstractUserInterface)
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)

    compiled_data, current_fiat_balance, total_balance = _get_compiled_balances(crypto_assets, fiat_asset)
    summary, rebalance, do_something = _compute_summary_and_rebalancing(crypto_assets, exposure, fiat_asset,
                                                                        fiat_decimals, compiled_data,
                                                                        total_balance)
    # show summary to user
    total_balance_str = f'{fiat_asset} {round(total_balance, fiat_decimals)}'
    user_interface.show_rebalance_summary(summary, total_balance_str)

    # if there is nothing to do, return
    if not do_something:
        return

    # request confirmation, there are pending actions
    if with_confirmation:
        confirmed = user_interface.request_confirmation('Proceed with rebalance?')
        if not confirmed:
            return

    real_amount_sold = current_fiat_balance
    required_amount_sold = current_fiat_balance

    # first sell operations
    for crypto_asset, data in rebalance.items():
        diff = data['diff']
        if diff < 0:
            continue
        quantity = abs(diff)
        if quantity < 10.0:
            continue
        try:
            user_interface.show_message(f'> Selling {fiat_asset} {quantity} of {crypto_asset}')
            required_amount_sold += abs(diff)
            exchange.place_fiat_sell_order(crypto_asset, quantity, fiat_asset)
            real_amount_sold += abs(diff)
        except Exception as e:
            user_interface.show_message(f'! Warning, error selling {crypto_asset}: {e}')
            continue

    if real_amount_sold == 0.0:
        user_interface.show_message(f'! Nothing sold. Exiting')
        return

    amount_sold_factor = real_amount_sold / required_amount_sold

    # second buy operations
    sorted_cryptos = sorted([k for k in rebalance.keys()], key=lambda key: rebalance[key]['diff'])
    for crypto_asset in sorted_cryptos:
        data = rebalance[crypto_asset]
        diff = data['diff']
        if diff > 0:
            continue
        for n in range(0, 50, 5):
            quantity = (abs(diff) - n) * amount_sold_factor
            if quantity > real_amount_sold:
                quantity = real_amount_sold
            if quantity < 10.0:
                break
            try:
                user_interface.show_message(f'> Buying {fiat_asset} {quantity} of {crypto_asset}')
                exchange.place_fiat_buy_order(crypto_asset, quantity, fiat_asset)
                break
            except Exception as e:
                user_interface.show_message(f'! Warning, error buying {crypto_asset}: {e}')
                continue

    # post operation get result
    compiled_data, current_fiat_balance, total_balance = _get_compiled_balances(crypto_assets, fiat_asset)
    for crypto_asset in crypto_assets:
        event_dispatcher.emit('crypto-asset-balance', **{
            'now': now,
            'crypto_asset': crypto_asset,
            'balance': compiled_data[crypto_asset]['balance'],
        })
    event_dispatcher.emit('total_balance', **{
        'now': now,
        'total_balance': total_balance,
    })


def _get_compiled_balances(crypto_assets, fiat_asset):
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)

    compiled_data = {}
    current_fiat_balance = exchange.get_asset_balance(asset=fiat_asset)
    total_balance = current_fiat_balance
    for crypto_asset in crypto_assets:
        balance = exchange.get_asset_balance(asset=crypto_asset)
        fiat_price = exchange.get_asset_fiat_price(asset=crypto_asset, fiat_asset=fiat_asset)
        total_balance += balance * fiat_price
        compiled_data[crypto_asset] = {
            'balance': balance,
            'avg_price': fiat_price,
            'fiat': balance * fiat_price,
        }
    return compiled_data, current_fiat_balance, total_balance


def _compute_summary_and_rebalancing(crypto_assets, exposure, fiat_asset, fiat_decimals, compiled_data, total_balance):
    do_something = False

    # equally distributed percentages between crypto assets
    percentage = (100.0 / len(crypto_assets)) * exposure
    summary = []
    rebalance = {}
    for crypto_asset in crypto_assets:
        wanted_fiat_balance = (percentage / 100) * total_balance
        current_fiat = compiled_data[crypto_asset]['fiat']
        diff = current_fiat - wanted_fiat_balance

        current_percentage = round((current_fiat / total_balance) * 100, 2)
        target_percentage = round(percentage, 2)
        diff_percentage = current_percentage - target_percentage

        row = [
            crypto_asset,
            f'{fiat_asset} {round(wanted_fiat_balance, fiat_decimals)}',
            f'{target_percentage}%',
            f'{fiat_asset} {round(current_fiat, fiat_decimals)}',
            f'{current_percentage}%',
        ]

        if abs(diff) <= 5.0:
            row.append(f'NOTHING')
        else:
            do_something = True
            if diff < 0:
                if -10.0 < diff < -5.0:
                    diff = -10.0
                row.append(f'BUY {fiat_asset} {abs(round(diff, fiat_decimals))}')
            else:
                if 10.0 > diff > 5.0:
                    diff = 10.0
                row.append(f'SELL {fiat_asset} {abs(round(diff, fiat_decimals))}')
        summary.append(row)
        rebalance[crypto_asset] = {
            'balance': compiled_data[crypto_asset]['balance'],
            'wanted_fiat': wanted_fiat_balance,
            'current_fiat': compiled_data[crypto_asset]['fiat'],
            'diff': diff,
            'diff_percentage': diff_percentage,
        }
    return summary, rebalance, do_something
