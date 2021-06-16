from core.domain.distribution import Distribution, EqualDistribution

fiat_asset = 'BUSD'
fiat_decimals = 2
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
exposure = 0.995  # max 0.995, min 0.005. Due to volatile nature of prices, a small margin should be left untouched.
distribution: Distribution = EqualDistribution(crypto_assets=crypto_assets)
