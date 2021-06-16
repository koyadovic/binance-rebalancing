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
exposure = 0.995
