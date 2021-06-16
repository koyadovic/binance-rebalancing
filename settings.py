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

"""
from all of your balance, control how much you are exposed with exposure setting. max 0.995, min 0.005
0.995 means all of your balance will be used for assets rebalancing
0.005 means nothing of your balance used.

with 0.5 you only expose the half of your balance.
If every crypto asset goes down, automatic buy will occur.
If every crypto asset goes up, automatic sell will occur.
Always keeping the proportions.

Example:
fiat_asset = 'BUSD'
fiat_decimals = 2
crypto_assets = ["BTC", "ETH"]
exposure = 0.5

This will keep for every execution:
- 50% in BUSD
- 25% in BTC
- 25% in ETH 
"""
exposure = 0.995
