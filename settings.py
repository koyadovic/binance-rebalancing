from core.domain.distribution import Distribution, EqualDistribution


crypto_assets = [
    'BTC',
    'ETH',
    'BNB',
    'ADA',
    'UNI',
    'VET',
    'DOT',
    'SOL',
    # 'AAVE',
    # 'NANO',
    'MATIC',
    # 'XLM',
    # 'EOS',
    'LINK',
    # 'ATOM',
]

fiat_asset = 'BUSD'
fiat_decimals = 2
fiat_untouched = float(len(crypto_assets) * 5)
exposure = 1.0  # max 1.0, min 0.0
distribution: Distribution = EqualDistribution(crypto_assets=crypto_assets)
