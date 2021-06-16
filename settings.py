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
exposure = 0.995
distribution: Distribution = EqualDistribution(crypto_assets=crypto_assets)
