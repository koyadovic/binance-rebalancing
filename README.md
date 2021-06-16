# Binance Rebalancing
This is a simple project that rebalance your binance portfolio configured into `settings.py` file. The current code only accepts Binance but could be easily extended to accept other exchanges as well.

## For users

Install everything with:
```bash
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

This was tested with Python 3.8.

Some common configurations that might be needed are exposed:

### Several crypto assets, same percentage for each one
Edit `settings.py` with something like:
```python
fiat_asset = 'BUSD'  # or 'USDT'
fiat_decimals = 2
crypto_assets = [
    'BTC',
    'ETH',
    # add here all your assets
]
exposure = 0.995  # max 0.995, min 0.005. Due to volatile nature of prices, a small margin should be left untouched.
distribution = EqualDistribution(crypto_assets=crypto_assets)
```
This will keep the two assets in the example, 50% for each one of them. If you add three assets, there will be 33.3% for each one. And so on for four, five .. 

### Only BTC but only 50% of my fiat exposed
Edit `settings.py` with something like:
```python
fiat_asset = 'BUSD'  # or 'USDT'
fiat_decimals = 2
crypto_assets = ['BTC']
exposure = 0.5  # max 0.995, min 0.005. Due to volatile nature of prices, a small margin should be left untouched.
distribution = EqualDistribution(crypto_assets=crypto_assets)
```
This will keep 50% of fiat untouched and the other 50% with BTC. You can get with this configuration automatic buys when BTC price goes down, causing fiat percentage to increase and BTC percentage to decrease and viceversa, automatic sells when BTC price goes up, for the inverse reason.

### I want 50% in BTC, 25% ETH and 25% in ADA
Edit `settings.py` with something like:
```python
fiat_asset = 'BUSD'  # or 'USDT'
fiat_decimals = 2
crypto_assets = ['BTC', 'ETH', 'ADA']
exposure = 0.995  # max 0.995, min 0.005. Due to volatile nature of prices, a small margin should be left untouched.
distribution = CustomDistribution(
    crypto_assets=crypto_assets,
    percentages={
        'BTC': 50,
        'ETH': 25,
        'ADA': 25
    }
)
```
With this configuration, on every rebalance will cause the needed buys and sells to keep always 50% on BTC, 25% on ETH and 25% on ADA.

## Environment variables
The default exchange implementation is for binance. This implementation need the following environment variables to be defined:

```bash
export BINANCE_API_KEY=<api_key>
export BINANCE_API_SECRET=<api_secret>
```

## Execution

Each execution, will retrieve what the crypto balances are and will ask you if you want to rebalance to keep the proportions specified in `settings.py` file.

```
$ python rebalance.py 
+--------+---------------+----------+---------------+-----------+--------------+
| Symbol | Wanted amount | Wanted % |    Current    | Current % |    Action    |
|        |               |          |    amount     |           |              |
+========+===============+==========+===============+===========+==============+
|  BTC   |    $464.48    |   50%    |     $0.0      |   0.0%    | BUY $464.48  |
+--------+---------------+----------+---------------+-----------+--------------+
|  ETH   |    $464.48    |   50%    |    $928.96    |  100.0%   | SELL $464.48 |
+--------+---------------+----------+---------------+-----------+--------------+
TOTAL BALANCE: $928.96

Proceed with rebalance?
(y/n) 
```

For a periodic rebalance you can use crontab with `bin/rebalance.sh` bash script. Create `.environment` file with the following content:

```bash
export BINANCE_API_KEY=<api_key>
export BINANCE_API_SECRET=<api_secret>
```

Then execute it. It will not ask for user confirmation, simply will rebalance all your portfolio with the configuration specified into `settings.py`.

## Crontab

Use something like this:

```bash
# m h  dom mon dow   command
0 * * * * /bin/bash <path_to_cloned_project>/bin/rebalance.sh
```

## Jupyter Notebooks
There is a couple of notebooks inside `notebooks/` folder. Just run `jupyter-lab` and browse `notebooks/`. For more information, read `notebooks/README.md` file. 

## For developers

### Change the default Binance exchange
If want to use Coinbase or another exchange, implement `core.domain.interfaces.AbstractExchange` inside `core.infrastructure` package. Then edit file `core/bootstrap.py` changing:
```python
# default implementation
dependency_dispatcher.register_implementation(
    AbstractExchange,
    BinanceExchange(
        api_key=os.environ.get('BINANCE_API_KEY'),
        api_secret=os.environ.get('BINANCE_API_SECRET'),
    )
)

# to something like
dependency_dispatcher.register_implementation(
    AbstractExchange,
    CoinbaseExchange(**your_kwargs)  # or whatever
)
```

### Use the core with a ncurses frontend or another GUI
Instead of running everything using rebalance.py and settings.py, could be feasible running everything from a GUI with persistent settings letting users control everything.
