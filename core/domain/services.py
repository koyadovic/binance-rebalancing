import itertools

from core.domain.distribution import Distribution
from core.domain.entities import Operation
from core.domain.exceptions import CannotExecuteOperation
from core.domain.interfaces import AbstractExchange, AbstractUserInterface, AbstractDebugPlatform
from core.domain.tools import number_similarity
from shared.domain.dependencies import dependency_dispatcher
from shared.domain.event_dispatcher import event_dispatcher

from datetime import datetime
import pytz


def rebalance(crypto_assets: list = None, fiat_asset: str = None,
              fiat_decimals: int = None, fiat_untouched: float = 0.0,
              exposure: float = None, with_confirmation=True, quiet=False,
              now=None, distribution: Distribution = None):

    now = now or datetime.utcnow().replace(tzinfo=pytz.utc)

    raise Exception('Test')

    # dependencies
    user_interface: AbstractUserInterface = dependency_dispatcher.request_implementation(AbstractUserInterface)
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)

    compiled_data, current_fiat_balance, total_balance = _get_compiled_balances(crypto_assets, fiat_asset, now)
    rebalance_data = _compute_rebalancing_data(crypto_assets, exposure, compiled_data, total_balance, distribution,
                                               fiat_untouched)

    # initial operations
    raw_operations = _transform_rebalance_data_into_operations(rebalance_data, fiat_asset)

    # default accepted operations by the exchange. This uses fiat by default
    # default_operations = exchange.get_exchange_valid_operations(raw_operations)
    # default_fees = exchange.compute_fees(default_operations, fiat_asset=fiat_asset, instant=now)

    # this try to use direct conversion between assets, if it exists
    final_operations = _try_to_use_direct_conversions_between_assets(raw_operations, fiat_asset, now)
    # final_fees = exchange.compute_fees(final_operations, fiat_asset=fiat_asset, instant=now)

    # show summary to user
    if with_confirmation or not quiet:
        headers = ['Symbol', 'Wanted amount', 'Wanted %', 'Current amount', 'Current %', 'Action']
        summary = []
        for asset, data in rebalance_data.items():
            row = [
                asset,
                f'{fiat_asset} {round(data["wanted_fiat"], fiat_decimals)}',
                f'{data["target_percentage"]}%',
                f'{fiat_asset} {round(data["current_fiat"], fiat_decimals)}',
                f'{data["current_percentage"]}%',
            ]
            for op in final_operations:
                if asset in [op.base_currency, op.quote_currency]:
                    row.append(str(op))
                    break
            else:
                row.append('NOTHING')
            summary.append(row)
        user_interface.show_table(
            headers=headers,
            rows=summary,
            total_balance=f'{fiat_asset} {round(total_balance, fiat_decimals)}',
            total_number_of_operations=f'{len(final_operations)}'
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
        for operation in unprocessed:
            quote_balance = exchange.get_asset_balance(operation.quote_currency)
            if quote_balance < operation.quote_amount:
                operation.quote_amount = exchange.get_asset_balance(operation.quote_currency)
                valid_operation = exchange.get_exchange_valid_operations([operation])
                result = exchange.execute_operations(valid_operation, fiat_asset=fiat_asset, instant=now)
                if len(valid_operation) > 0 and len(result) > 0:
                    raise CannotExecuteOperation(f'Cannot process operation {operation}')

    compiled_data, current_fiat_balance, total_balance = _get_compiled_balances(crypto_assets, fiat_asset, now)
    for crypto_asset in crypto_assets:
        event_dispatcher.emit('crypto-asset-balance', **{
            'now': now,
            'crypto_asset': crypto_asset,
            'balance': compiled_data[crypto_asset]['balance'],
        })
    event_dispatcher.emit('total-balance', **{
        'now': now,
        'fiat_asset': fiat_asset,
        'total_balance': total_balance,
    })


def _try_to_use_direct_conversions_between_assets(raw_operations, fiat_asset, now):
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)
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
            if not exchange.exchange_pair_exist(buy_operation.base_currency, sell_operation.base_currency) and \
                    not exchange.exchange_pair_exist(sell_operation.base_currency, buy_operation.base_currency):
                continue
            if buy_operation.base_currency in quote_assets and sell_operation.base_currency in quote_assets:
                continue
            if buy_operation.base_currency not in quote_assets and sell_operation.base_currency not in quote_assets:
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
    return final_operations


def _get_quote_assets(buy_operations, sell_operations):
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)
    quote_assets = set()
    for buy_operation, sell_operation in iter(itertools.product(buy_operations, sell_operations)):
        if exchange.exchange_pair_exist(buy_operation.base_currency, sell_operation.base_currency):
            quote_assets.add(sell_operation.base_currency)
        if exchange.exchange_pair_exist(sell_operation.base_currency, buy_operation.base_currency):
            quote_assets.add(buy_operation.base_currency)
    return quote_assets


def _split_buy_and_sell_operations(operations):
    sell_operations, buy_operations = [], []
    for op in operations:
        if op.type == Operation.TYPE_SELL:
            sell_operations.append(op)
        else:
            buy_operations.append(op)
    return buy_operations, sell_operations


def _get_compiled_balances(crypto_assets, fiat_asset, instant):
    exchange: AbstractExchange = dependency_dispatcher.request_implementation(AbstractExchange)

    compiled_data = {}
    current_fiat_balance = exchange.get_asset_balance(asset=fiat_asset)
    total_balance = current_fiat_balance
    for crypto_asset in crypto_assets:
        balance = exchange.get_asset_balance(asset=crypto_asset)
        fiat_price = exchange.get_asset_price(base_asset=crypto_asset, quote_asset=fiat_asset, instant=instant)
        fiat_balance = balance * fiat_price
        total_balance += fiat_balance
        compiled_data[crypto_asset] = {
            'balance': balance,
            'avg_price': fiat_price,
            'fiat': fiat_balance,
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
            'current_percentage': current_percentage,
            'target_percentage': target_percentage,
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
