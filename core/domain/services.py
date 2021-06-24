from datetime import datetime
from typing import List

import pytz

from core.domain.distribution import Distribution
from core.domain.entities import Operation
from core.domain.interfaces import AbstractExchange, AbstractUserInterface
from shared.domain.dependencies import dependency_dispatcher
from shared.domain.event_dispatcher import event_dispatcher


def number_similarity(n1, n2):
    ns = [n1, n2]
    return min(ns) / max(ns)


def rebalance(crypto_assets: list = None, fiat_asset: str = None,
              fiat_decimals: int = None, fiat_untouched: float = 0.0,
              exposure: float = None, with_confirmation=True, quiet=False,
              now=None, distribution: Distribution = None):

    now = now or datetime.utcnow().replace(tzinfo=pytz.utc)

    # dependencies
    user_interface: AbstractUserInterface = dependency_dispatcher.request_implementation(AbstractUserInterface)
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)

    compiled_data, current_fiat_balance, total_balance = _get_compiled_balances(crypto_assets, fiat_asset, now)
    rebalance_data = _compute_rebalancing_data(crypto_assets, exposure, compiled_data, total_balance, distribution,
                                               fiat_untouched)

    raw_operations = _transform_rebalance_data_into_operations(rebalance_data, fiat_asset)
    default_operations = exchange.get_exchange_valid_operations(raw_operations)
    default_fees = exchange.compute_fees(default_operations, fiat_asset=fiat_asset)

    # while True:
    #     # TODO las conversiones han de producirse aquí.
    #     #  Tenemos que conseguir rebalanceo reduciendo final_fees por debajo de default_fees
    #     raw_buy_operations, raw_sell_operations = _split_buy_and_sell_operations(raw_operations)
    #
    #     converted_operations = raw_sell_operations + raw_buy_operations
    #     final_operations = exchange.get_exchange_valid_operations(converted_operations)
    #     final_fees = exchange.compute_fees(final_operations, fiat_asset=fiat_asset)
    #     if final_fees < default_fees:
    #         break

    # TODO show summary to user
    # if with_confirmation or not quiet:
    #     summary = _build_summary(operations)
    #     total_balance_str = f'{fiat_asset} {round(total_balance, fiat_decimals)}'
    #     user_interface.show_rebalance_summary(summary, total_balance_str)

    # if there is nothing to do, return
    if len(default_operations) == 0:
        return

    # request confirmation, there are pending actions
    if with_confirmation:
        confirmed = user_interface.request_confirmation('Proceed with rebalance?')
        if not confirmed:
            return

    exchange.execute_operations(default_operations)

    # Obsolete
    # rebalance_execution(crypto_assets, fiat_asset, fiat_decimals, current_fiat_balance, rebalance_data, now,
    #                     with_confirmation, quiet)


def _split_buy_and_sell_operations(operations):
    sell_operations = [op for op in operations if op.type == Operation.TYPE_SELL]
    buy_operations = [op for op in operations if op.type == Operation.TYPE_BUY]
    return buy_operations, sell_operations


def _get_compiled_balances(crypto_assets, fiat_asset, instant):
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)

    compiled_data = {}
    current_fiat_balance = exchange.get_asset_balance(asset=fiat_asset)
    total_balance = current_fiat_balance
    for crypto_asset in crypto_assets:
        balance = exchange.get_asset_balance(asset=crypto_asset)
        fiat_price = exchange.get_asset_price(base_asset=crypto_asset, quote_asset=fiat_asset, instant=instant)
        total_balance += balance * fiat_price
        compiled_data[crypto_asset] = {
            'balance': balance,
            'avg_price': fiat_price,
            'fiat': balance * fiat_price,
        }
    return compiled_data, current_fiat_balance, total_balance


def _compute_rebalancing_data(crypto_assets, exposure, compiled_data, total_balance, distribution, fiat_untouched):
    total_balance_without_tiny_fiat = total_balance - fiat_untouched
    rebalance_data = {}
    for crypto_asset in crypto_assets:
        percentage = distribution.assign_percentage(crypto_asset) * exposure
        wanted_fiat_balance = (percentage / 100) * total_balance_without_tiny_fiat
        current_fiat = compiled_data[crypto_asset]['fiat']
        avg_price = compiled_data[crypto_asset]['avg_price']
        diff = current_fiat - wanted_fiat_balance

        current_percentage = round((current_fiat / total_balance_without_tiny_fiat) * 100, 2)
        target_percentage = round(percentage, 2)
        diff_percentage = current_percentage - target_percentage

        rebalance_data[crypto_asset] = {
            'avg_price': avg_price,
            'balance': compiled_data[crypto_asset]['balance'],
            'wanted_fiat': wanted_fiat_balance,
            'current_fiat': compiled_data[crypto_asset]['fiat'],
            'diff': diff,
            'diff_percentage': diff_percentage,
        }

    return rebalance_data


def _transform_rebalance_data_into_operations(rebalance_data, fiat_asset):
    operations = []
    for crypto_asset, data in rebalance_data.items():
        diff = data['diff']
        if diff > 0:
            o = Operation(pair=f'{crypto_asset}/{fiat_asset}', type=Operation.TYPE_SELL, quote_amount=abs(diff))
            operations.append(o)
        elif diff < 0:
            o = Operation(pair=f'{crypto_asset}/{fiat_asset}', type=Operation.TYPE_BUY, quote_amount=abs(diff))
            operations.append(o)
    return operations


def _build_summary(operations: List[Operation]):
    # TODO build summary

    summary = []
    for operation in operations:
        row = [
            operation.pair,
            f'{fiat_asset} {round(wanted_fiat_balance, fiat_decimals)}',
            f'{target_percentage}%',
            f'{fiat_asset} {round(current_fiat, fiat_decimals)}',
            f'{current_percentage}%',
        ]
        if abs(diff) <= 5.0:
            row.append(f'NOTHING')
        else:
            if diff < 0:
                if -10.0 < diff < -5.0:
                    diff = -10.0
                row.append(f'BUY {fiat_asset} {abs(round(diff, fiat_decimals))}')
            else:
                if 10.0 > diff > 5.0:
                    diff = 10.0
                row.append(f'SELL {fiat_asset} {abs(round(diff, fiat_decimals))}')
        summary.append(row)
    return summary


# def rebalance_execution(crypto_assets, fiat_asset, fiat_decimals, current_fiat_balance, rebalance_data, now,
#                         with_confirmation, quiet):
#     # dependencies
#     user_interface: AbstractUserInterface = dependency_dispatcher.request_implementation(AbstractUserInterface)
#     exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)
#
#     real_amount_sold = current_fiat_balance
#     required_amount_sold = current_fiat_balance
#
#     # first sell operations
#     for crypto_asset, data in rebalance_data.items():
#         diff = data['diff']
#         avg_price = data['avg_price']
#         if diff < 0:
#             continue
#         quantity = abs(diff)
#         if quantity < 10.0:
#             continue
#         try:
#             if with_confirmation or not quiet:
#                 user_interface.show_message(f'> Selling {fiat_asset} {quantity} of {crypto_asset}')
#             required_amount_sold += abs(diff)
#             exchange.place_sell_order(crypto_asset, fiat_asset, quantity, avg_price=avg_price)
#             real_amount_sold += abs(diff)
#         except Exception as e:
#             user_interface.show_message(f'! Warning, error selling {crypto_asset}: {e}')
#             continue
#
#     if real_amount_sold == 0.0:
#         user_interface.show_message(f'! Nothing sold. Exiting')
#         return
#
#     amount_sold_factor = real_amount_sold / required_amount_sold
#
#     # second buy operations
#     sorted_cryptos = sorted([k for k in rebalance_data.keys()], key=lambda key: rebalance_data[key]['diff'])
#     for crypto_asset in sorted_cryptos:
#         data = rebalance_data[crypto_asset]
#         diff = data['diff']
#         avg_price = data['avg_price']
#         fiat_balance = exchange.get_asset_balance(fiat_asset)
#         if fiat_balance < 10.0:
#             break
#         if diff > 0:
#             continue
#         for n in range(0, 50, 5):
#             quantity = (abs(diff) - n) * amount_sold_factor
#             if quantity > real_amount_sold:
#                 quantity = real_amount_sold
#             if quantity < 10.0:
#                 break
#             quantity = int(quantity * (10 ** fiat_decimals)) / (10 ** fiat_decimals)
#             try:
#                 if with_confirmation or not quiet:
#                     user_interface.show_message(f'> Buying {fiat_asset} {quantity} of {crypto_asset}')
#
#                 if quantity > fiat_balance:
#                     quantity = fiat_balance
#                 exchange.place_buy_order(crypto_asset, fiat_asset, quantity, avg_price=avg_price)
#                 break
#
#             except Exception as e:
#                 user_interface.show_message(f'! Warning, error buying {crypto_asset}: {e}')
#                 continue
#
#     # post operation emit events with updated balances
#     compiled_data, current_fiat_balance, total_balance = _get_compiled_balances(crypto_assets, fiat_asset, now)
#     for crypto_asset in crypto_assets:
#         event_dispatcher.emit('crypto-asset-balance', **{
#             'now': now,
#             'crypto_asset': crypto_asset,
#             'balance': compiled_data[crypto_asset]['balance'],
#         })
#     event_dispatcher.emit('total-balance', **{
#         'now': now,
#         'fiat_asset': fiat_asset,
#         'total_balance': total_balance,
#     })
