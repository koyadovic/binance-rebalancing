import csv
import itertools
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import timedelta, datetime
from core.bootstrap import init_core_module_for_simulations
from core.domain import services as rebalancing_services
from core.domain.distribution import EqualDistribution
from shared.domain.dependencies import dependency_dispatcher


assets = [
    'BTC',
    'ETH',
    'BNB',
    'VET',
    'ADA',
    'EOS',
    'MATIC',
    'NANO',
    'XLM',
    'ATOM',
    'LINK',
    'LTC',

    # 'UNI',
    # 'DOT',
    # 'SOL',
    # 'AAVE',

]
# day_ranges = [90, 180, 360]
day_ranges = [180]
periods = {
    '1h': timedelta(hours=1),
    '1d': timedelta(days=1),
    '1w': timedelta(days=7),
}

exposures = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
exposures.reverse()
initial_fiat_investments = [5000, 10000, 20000]


def get_all_assets_combinations(required=None):
    for n in range(len(assets)):
        for combination in list(itertools.combinations(assets, n + 1)):
            current_combination = list(combination)
            if required is not None:
                valid = True
                for asset_required in required:
                    valid = valid and asset_required in current_combination
                if not valid:
                    continue
            yield current_combination


# simulation date ranges
starting_date = datetime(2019, 8, 1, 0, 0, 0)
ending_date = datetime(2021, 6, 1, 0, 0, 0)


simulation_dates = []
for day_range in day_ranges:
    start = starting_date
    while True:
        end = start + timedelta(days=day_range)
        if end > ending_date:
            break
        simulation_dates.append((start, end, f'{day_range}'))
        start += timedelta(days=30)

fiat_asset = 'USDT'
fiat_decimals = 2

exchange = None


def process_completed_results(lst_completed_results):
    if len(lst_completed_results) > 0:
        with open('simulation.csv', mode='a') as simulation_file:
            simulation_writer = csv.writer(simulation_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for completed_result in lst_completed_results:
                simulation_writer.writerow(completed_result)


def main():
    global exchange
    init_core_module_for_simulations()

    from core.domain.interfaces import AbstractExchange
    exchange = dependency_dispatcher.request_implementation(AbstractExchange)

    # maybe we can use this data for the study
    # read activity/README.md
    # init_activity_module()
    # all_assets_combinations = list(get_all_assets_combinations(required=['BTC', 'BNB', 'ETH']))

    with open('simulation.csv', mode='w') as simulation_file:
        simulation_writer = csv.writer(simulation_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        simulation_writer.writerow([
            'Start', 'End', 'Tag', 'No. Assets', 'Assets', 'Period', 'Exposure',
            'Rebalance Fiat Balance', 'HODL Fiat Balance',
            'Rebalance Profit', 'HODL Profit', 'Profit related to HODL strategy',
        ])

    all_assets_combinations = list(get_all_assets_combinations())
    pending_tasks_args = []
    for start_date, end_date, tag in simulation_dates:
        for initial_fiat_invest in initial_fiat_investments:
            for exposure in exposures:
                for current_assets in all_assets_combinations:
                    for period in periods.keys():
                        args = (start_date, end_date, current_assets, initial_fiat_invest, exposure, period, tag)
                        pending_tasks_args.append(args)

    max_tasks_in_queue = 300
    total_n = len(pending_tasks_args)
    current_n = 0

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count() - 1) as executor:
        # Set for the jobs created
        jobs = set()
        start_time = time.time()

        while len(pending_tasks_args) > 0 or len(jobs) > 0:
            while len(jobs) < max_tasks_in_queue:
                try:
                    args = pending_tasks_args.pop(0)
                    current_n += 1

                    # Single process. Use this and comment multiprocessing below to debug with ipdb.
                    # process_completed_results([_processing_function(*args)])

                    # Multiprocessing
                    job = executor.submit(_processing_function, *args)
                    jobs.add(job)

                    if len(jobs) > max_tasks_in_queue:
                        break
                except IndexError:
                    break

            completed_jobs = []
            completed_results = []
            for job in as_completed(jobs):
                job_result = job.result()
                completed_results.append(job_result)
                completed_jobs.append(job)

            process_completed_results(completed_results)

            for completed_job in completed_jobs:
                jobs.remove(completed_job)

            if len(completed_jobs) > 0:
                current_time = time.time()
                days, hours, minutes, seconds = _compute_eta(start_time, current_time, total_n, current_n)
                print(f'- {current_n}/{total_n} - ETA: {_eta_to_string(days, hours, minutes, seconds)}')


def _processing_function(start_date, end_date, current_assets, initial_fiat_invest, exposure, period, tag):
    distributor = EqualDistribution(crypto_assets=current_assets)
    now = start_date

    fiat_untouched = len(current_assets) * 6.0

    exchange.reset_balances(fiat_asset, initial_fiat_invest)
    have_hodl_balances = False
    hodl_balances = {}

    # reset all exchange data.
    # set initial fiat investment.
    while now < end_date:
        # empezar en el día que sea, e iterar periodo a periodo rebalanceando
        # los resultados tendrían que ser volcados a un CSV con las columnas:

        rebalancing_services.rebalance(
            crypto_assets=current_assets,
            fiat_asset=fiat_asset,
            fiat_decimals=fiat_decimals,
            fiat_untouched=fiat_untouched,
            exposure=exposure,
            with_confirmation=False,
            now=now,
            distribution=distributor,
            quiet=True
        )

        if not have_hodl_balances:
            hodl_balances = {fiat_asset: 0.0}
            for asset in current_assets:
                fiat_for_asset = (distributor.assign_percentage(asset) / 100) * initial_fiat_invest
                asset_price = exchange.get_asset_price(asset, fiat_asset, instant=now)
                # 0.999 is for binance fees
                hodl_balances[asset] = (fiat_for_asset * 0.999) / asset_price
            have_hodl_balances = True

        now += periods[period]

    if now > end_date:
        now = end_date
        rebalancing_services.rebalance(
            crypto_assets=current_assets,
            fiat_asset=fiat_asset,
            fiat_decimals=fiat_decimals,
            fiat_untouched=fiat_untouched,
            exposure=exposure,
            with_confirmation=False,
            now=now,
            distribution=distributor,
            quiet=True
        )

    # save all produced data to use later for the study
    last_execution_balances = dict(exchange.balances)
    hodl_total_fiat_balance = compute_fiat_balance(hodl_balances, now)
    rebalance_fiat_balance = compute_fiat_balance(last_execution_balances, now)

    hodl_profit = round(((hodl_total_fiat_balance - initial_fiat_invest) / initial_fiat_invest) * 100, 2)
    rebalance_profit = round(((rebalance_fiat_balance - initial_fiat_invest) / initial_fiat_invest) * 100, 2)
    diff_profit = ((rebalance_fiat_balance - hodl_total_fiat_balance) / hodl_total_fiat_balance) * 100.0
    row = [
        starting_date, end_date, tag,
        len(current_assets), ','.join(current_assets),
        period, exposure,
        rebalance_fiat_balance, hodl_total_fiat_balance,
        rebalance_profit, hodl_profit, diff_profit,
    ]
    return row


def compute_fiat_balance(balances, now):
    total_fiat_balance = balances.get(fiat_asset, 0.0)
    for asset, balance in balances.items():
        if asset == fiat_asset:
            continue
        total_fiat_balance += exchange.get_asset_price(asset, fiat_asset, instant=now) * balance
    return total_fiat_balance


def _eta_to_string(days, hours, minutes, seconds):
    parts = []
    if days != 0:
        parts.append(f'{days} days')
    if hours != 0:
        parts.append(f'{str(hours).zfill(2)} hours')
    if minutes != 0:
        parts.append(f'{str(minutes).zfill(2)} minutes')
    parts.append(f'{str(seconds).zfill(2)} seconds')
    return ' '.join(parts) + ' ...'


def _compute_eta(start_time, current_time, total, cycles_done):
    seconds = current_time - start_time
    seconds_per_cycle = seconds / cycles_done
    pending_seconds = seconds_per_cycle * (total - cycles_done)
    days = int(pending_seconds // (3600 * 24))
    hours = int((pending_seconds - (days * 3600 * 24)) // 3600)
    minutes = int((pending_seconds - (days * 3600 * 24) - (hours * 3600)) // 60)
    seconds = int(pending_seconds - (days * 3600 * 24) - (hours * 3600) - (minutes * 60))
    return days, hours, minutes, seconds


if __name__ == '__main__':
    main()
