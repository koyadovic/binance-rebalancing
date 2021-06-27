import json
import logging
from datetime import datetime
from typing import List

import pytz

from core.domain.distribution import Distribution
from core.domain.entities import Operation
from core.domain.interfaces import AbstractExchange, AbstractUserInterface, CannotProcessOperation
from shared.domain.dependencies import dependency_dispatcher
from shared.domain.event_dispatcher import event_dispatcher


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()


def rebalance(crypto_assets: list = None, fiat_asset: str = None,
              fiat_decimals: int = None, fiat_untouched: float = 0.0,
              exposure: float = None, with_confirmation=True, quiet=False,
              now=None, distribution: Distribution = None):

    now = now or datetime.utcnow().replace(tzinfo=pytz.utc)

    logger.info(f'rebalance at {now}: {crypto_assets}, {fiat_asset}, {fiat_decimals}, {fiat_untouched}, {exposure}')

    # dependencies
    user_interface: AbstractUserInterface = dependency_dispatcher.request_implementation(AbstractUserInterface)
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)

    compiled_data, current_fiat_balance, total_balance = _get_compiled_balances(crypto_assets, fiat_asset, now)
    rebalance_data = _compute_rebalancing_data(crypto_assets, exposure, compiled_data, total_balance, distribution,
                                               fiat_untouched)

    raw_operations = _transform_rebalance_data_into_operations(rebalance_data, fiat_asset)
    default_operations = exchange.get_exchange_valid_operations(raw_operations)
    default_fees = exchange.compute_fees(default_operations, fiat_asset=fiat_asset, instant=now)

    raw_buy_operations, raw_sell_operations = _split_buy_and_sell_operations(raw_operations)

    # first we extract valid quote_assets for this exchange
    quote_assets = _get_quote_assets(raw_buy_operations, raw_sell_operations)

    deviations = {}
    for buy_operation in raw_buy_operations:
        if buy_operation.base_currency not in deviations:
            deviations[buy_operation.base_currency] = -buy_operation.quote_amount
    for sell_operation in raw_sell_operations:
        if sell_operation.base_currency not in deviations:
            deviations[sell_operation.base_currency] = sell_operation.quote_amount

    # try to pair operations
    pairs = []
    for buy_operation in raw_buy_operations:
        if deviations[buy_operation.base_currency] >= 0:
            continue
        most_similar_sell = None
        for sell_operation in raw_sell_operations:
            if deviations[sell_operation.base_currency] <= 0:
                continue
            if buy_operation.base_currency in quote_assets and sell_operation.base_currency in quote_assets:
                continue
            if buy_operation.base_currency not in quote_assets and sell_operation.base_currency not in quote_assets:
                continue
            if not exchange.exchange_pair_exist(buy_operation.base_currency, sell_operation.base_currency) and \
                    not exchange.exchange_pair_exist(sell_operation.base_currency, buy_operation.base_currency):
                continue
            if most_similar_sell is None:
                most_similar_sell = sell_operation
            else:
                current_sim = number_similarity(buy_operation.quote_amount, sell_operation.quote_amount)
                current_best_sim = number_similarity(buy_operation.quote_amount, most_similar_sell.quote_amount)
                if current_sim > current_best_sim:
                    most_similar_sell = sell_operation

        if most_similar_sell is None:
            for sell_operation in raw_sell_operations:
                if deviations[sell_operation.base_currency] <= 0:
                    continue
                if not exchange.exchange_pair_exist(buy_operation.base_currency, sell_operation.base_currency) and \
                        not exchange.exchange_pair_exist(sell_operation.base_currency, buy_operation.base_currency):
                    continue
                if most_similar_sell is None:
                    most_similar_sell = sell_operation
                else:
                    current_sim = number_similarity(buy_operation.quote_amount, sell_operation.quote_amount)
                    current_best_sim = number_similarity(buy_operation.quote_amount, most_similar_sell.quote_amount)
                    if current_sim > current_best_sim:
                        most_similar_sell = sell_operation

        if most_similar_sell is not None:
            minimum_fiat = min([most_similar_sell.quote_amount, buy_operation.quote_amount])
            deviations[most_similar_sell.base_currency] -= minimum_fiat
            deviations[buy_operation.base_currency] += minimum_fiat
            pairs.append((buy_operation, most_similar_sell))

    # then add pending Operations not referenced by this pairs.
    converted_operations = []
    for buy_operation in raw_buy_operations:
        if buy_operation in [pair[0] for pair in pairs]:
            continue
        converted_operations.append(buy_operation)
        deviations[buy_operation.base_currency] += buy_operation.quote_amount
    for sell_operation in raw_sell_operations:
        if sell_operation in [pair[1] for pair in pairs]:
            continue
        converted_operations.append(sell_operation)
        deviations[sell_operation.base_currency] -= sell_operation.quote_amount

    # now we need to convert each pair in pairs, into a single Operation instance.
    for buy, sell in pairs:
        buy_operation = buy.clone()
        sell_operation = sell.clone()
        minimum_fiat = min([buy_operation.quote_amount, sell_operation.quote_amount])
        sell_operation.quote_amount = minimum_fiat
        buy_operation.quote_amount = minimum_fiat

        if exchange.exchange_pair_exist(buy_operation.base_currency, sell_operation.base_currency):
            base_asset = buy_operation.base_currency
            quote_asset = sell_operation.base_currency
            operation_type = Operation.TYPE_BUY
        elif exchange.exchange_pair_exist(sell_operation.base_currency, buy_operation.base_currency):
            base_asset = sell_operation.base_currency
            quote_asset = buy_operation.base_currency
            operation_type = Operation.TYPE_SELL
        else:
            continue
        quote_price = exchange.get_asset_price(quote_asset, fiat_asset, instant=now)
        operation = Operation(
            pair=f'{base_asset}/{quote_asset}',
            type=operation_type,
            quote_amount=minimum_fiat / quote_price
        )
        valid = exchange.get_exchange_valid_operations([operation])
        try:
            converted_operations.append(valid[0])
        except IndexError:
            # Operación única no válida. Revierte deviations con buy and sell
            deviations[sell.base_currency] += minimum_fiat
            deviations[buy.base_currency] -= minimum_fiat

    # repasa deviations y añade operaciones que aún no existan
    final_operations = exchange.get_exchange_valid_operations(converted_operations)
    for op in final_operations:
        if op.base_currency in deviations:
            if op.type == Operation.TYPE_BUY and deviations[op.base_currency] > 0:
                del deviations[op.base_currency]
            elif op.type == Operation.TYPE_SELL and deviations[op.base_currency] < 0:
                del deviations[op.base_currency]
        if op.quote_currency in deviations:
            if op.type == Operation.TYPE_BUY and deviations[op.quote_currency] < 0:
                del deviations[op.quote_currency]
            elif op.type == Operation.TYPE_SELL and deviations[op.quote_currency] > 0:
                del deviations[op.quote_currency]
    for asset, deviation in deviations.items():
        if deviation < 0:
            type_ = Operation.TYPE_BUY
        elif deviation > 0:
            type_ = Operation.TYPE_SELL
        else:
            continue
        final_operations.append(Operation(pair=f'{asset}/{fiat_asset}', type=type_, quote_amount=abs(deviation)))

    # to finalize this, get_exchange_valid_operations will return the valid ones.
    final_operations = sorted(
        exchange.get_exchange_valid_operations(final_operations),
        key=lambda o: (o.type, o.quote_amount),
        reverse=True
    )
    final_fees = exchange.compute_fees(final_operations, fiat_asset=fiat_asset, instant=now)

    # show summary to user
    if with_confirmation or not quiet:
        user_interface.show_table(
            headers=['Pair', 'Operation Type', 'Amount'],
            rows=[[op.pair, op.type, f'{op.quote_currency} {op.quote_amount}'] for op in final_operations],
            default_FEES=f'{fiat_asset} {default_fees}',
            final_FEES=f'{fiat_asset} {final_fees}',
        )

    # if there is nothing to do, return
    if len(final_operations) == 0:
        return

    # request confirmation, there are pending actions
    if with_confirmation:
        confirmed = user_interface.request_confirmation('Proceed with rebalance?')
        if not confirmed:
            return

    unprocessed = exchange.execute_operations(final_operations, fiat_asset=fiat_asset, instant=now)
    if len(unprocessed) > 0:
        print(f'now: {now}')
        print(f'current_fiat_balance: {current_fiat_balance}')
        print(f'crypto_assets: {crypto_assets}')
        print(f'fiat_untouched: {fiat_untouched}')
        print(f'exposure: {exposure}')
        print(f'rebalance_data: {json.dumps(rebalance_data)}')
        print(f'Default operations: {default_operations}')
        print(f'Final operations: {final_operations}')
        for operation in unprocessed:
            quote_balance = exchange.get_asset_balance(operation.quote_currency)
            if quote_balance < operation.quote_amount:
                operation.quote_amount = exchange.get_asset_balance(operation.quote_currency)
                valid_operation = exchange.get_exchange_valid_operations([operation])
                result = exchange.execute_operations(valid_operation, fiat_asset=fiat_asset, instant=now)
                if len(valid_operation) > 0 and len(result) == 0:
                    print(f'{valid_operation[0]} REALIZADA')
        print(f'=' * 80)


def _get_quote_assets(buy_operations, sell_operations):
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)
    quote_assets = []
    for buy_operation in buy_operations:
        if buy_operation.base_currency in quote_assets:
            continue
        for sell_operation in sell_operations:
            if sell_operation.base_currency in quote_assets:
                continue
            if exchange.exchange_pair_exist(buy_operation.base_currency, sell_operation.base_currency):
                quote_assets.append(sell_operation.base_currency)
            if exchange.exchange_pair_exist(sell_operation.base_currency, buy_operation.base_currency):
                quote_assets.append(buy_operation.base_currency)
    return quote_assets


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


def number_similarity(n1, n2):
    ns = [n1, n2]
    return min(ns) / max(ns)


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
