# Binance Rebalancing
This is a simple project that rebalance your binance portfolio configured into settings.py file.

Configure your assets as something like this:

```
portfolio_setting = {
    'BTC': 50,
    'ETH': 50,
}
```

Each execution, will retrieve what are their balances and will ask you if want to rebalance to keep the weight of each of your cryptocurrencies to the percentages specified.

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
