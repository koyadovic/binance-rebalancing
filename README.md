# Binance Rebalancing
This is a simple project that rebalance your binance portfolio configured into settings.py file.

Configure your assets as something like this:

```
portfolio_setting = {
    'BTC': 33.3,
    'ETH': 33.3,
    'LTC': 33.3
}
```

Each execution, will retrieve what are their balances and will ask you if want to rebalance to keep the weight of each of your cryptocurrencies to the percentages specified.
