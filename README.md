# Binance Rebalancing
This is a simple project that rebalance your binance portfolio configured into settings.py file.

See `settings.py` file for more information.

# Environment variables
The default binance implementation need the following environment variables to be defined

```
export BINANCE_API_KEY=<api_key>
export BINANCE_API_SECRET=<api_secret>
```

# Execution

Each execution, will retrieve what the crypto balances are and will ask if you want to rebalance to keep the same weight of each of them.

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

```
export BINANCE_API_KEY=<api_key>
export BINANCE_API_SECRET=<api_secret>
```

Then execute it. It will not ask for user confirmation, simply will rebalance all your portfolio with the configuration specified into `settings.py`.

# Crontab

Use something like this:

```
# m h  dom mon dow   command
0 * * * * /bin/bash <path_to_cloned_project>/bin/rebalance.sh
```
