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
TOTAL BALANCE: $928.96
+--------+---------------+----------+---------------+-----------+--------------+
| Symbol | Wanted amount | Wanted % |    Current    | Current % |    Action    |
|        |               |          |    amount     |           |              |
+========+===============+==========+===============+===========+==============+
|  BTC   |    $464.48    |   50%    |     $0.0      |   0.0%    | BUY $464.48  |
+--------+---------------+----------+---------------+-----------+--------------+
|  ETH   |    $464.48    |   50%    |    $928.96    |  100.0%   | SELL $464.48 |
+--------+---------------+----------+---------------+-----------+--------------+

Proceed with rebalance?
(y/n) 
```
