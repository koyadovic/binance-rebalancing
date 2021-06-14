import os

API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')


"""
Fiat asset selected. Use BUSD, USDT, and so on
"""

fiat_asset = 'BUSD'
fiat_decimals = 2

"""
Crypto assets
"""

crypto_assets = [
    'BTC',
    'ETH',
    'BNB',
    # 'ADA',
    # 'UNI',
    # 'VET',
    # 'DOT',
    # 'SOL',
    # 'AAVE',
    # 'NANO',
    # 'MATIC',
    # 'XLM',
    # 'EOS',
    # 'LINK',
    # 'ATOM',
]

# from all of your balance, control how much you are exposed with this setting. max 0.995, min 0.005
# 0.995 means all of your balance will be used for assets rebalancing
# 0.005 means nothing of your balance used.
exposure = 0.5

# automatically compute percentage for the number of assets selected, and use exposure to modify it.
percentage = 100.0 / len(crypto_assets)
portfolio_setting = {asset: percentage * exposure for asset in crypto_assets}


# Percentage of deviation to rebalance. Set to None if want to disable it
# for 1.0 value if asset has 10%, causes rebalancing if it takes >=11% or <=9%
# minimum_percentage_deviation = 1.0 * exposure
minimum_percentage_deviation = None
