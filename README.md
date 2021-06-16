# Binance Rebalancing
This is a simple project that rebalance your binance portfolio configured into `settings.py` file.

You must set:
```python
fiat_asset = 'BUSD'  # or USDT, etc
fiat_decimals = 2
```

Then select what are your assets:

```python
crypto_assets = [
    'BTC',
    'ETH'
]
```

Set also `exposure` variable:
```python
exposure = 0.995
```

With `exposure` variable you control how much are you exposed. Recommended max 0.995 and min 0.005.

- 0.995 means all of your balance will be used for assets rebalancing.

- 0.005 means nothing of your balance used.

With 0.5 you only expose the half of your balance.
If every crypto asset goes down, automatic buy will occur.
If every crypto asset goes up, automatic sell will occur.
Always keeping the proportions.

### Example:
```python
fiat_asset = 'BUSD'
fiat_decimals = 2
crypto_assets = ["BTC", "ETH"]
exposure = 0.5

distribution: Distribution = EqualDistribution(crypto_assets=crypto_assets)  # later explained
```

This will keep for every execution:
- 50% in BUSD
- 25% in BTC
- 25% in ETH

### Distributors

### - EqualDistribution
This distributor will assign the same percentage to each of your assets automatically.
```python
from core.domain.distribution import Distribution, EqualDistribution

distribution: Distribution = EqualDistribution(crypto_assets=crypto_assets)
```

### - CustomDistribution
This distributor will assign custom percentages for each asset. You must specify all of them
```python
from core.domain.distribution import Distribution, CustomDistribution

distribution: Distribution = CustomDistribution(
    crypto_assets=crypto_assets,
    percentages={
        'BTC': 75.0,
        'ETH': 25.0,
    }
)
```

See `settings.py` file for the initial idea.

# Environment variables
The default exchange implementation is for binance. This implementation need the following environment variables to be defined:

```bash
export BINANCE_API_KEY=<api_key>
export BINANCE_API_SECRET=<api_secret>
```

# Execution

Each execution, will retrieve what the crypto balances are and will ask you if you want to rebalance to keep the proportions specified by the `distributor` selected in `settings.py` file.

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

# Crontab

Use something like this:

```bash
# m h  dom mon dow   command
0 * * * * /bin/bash <path_to_cloned_project>/bin/rebalance.sh
```
