import math
import os

API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')

"""
Crypto: Percentage
"""

percentage = float(math.floor(100 / 3))

# leaving a tiny piece of fiat untouched
exposure = 0.5
# exposure = 0.995  # Recommended max 0.995, min 0.005
# exposure = 0.005

portfolio_setting = {
    # 'ADA': percentage * exposure,
    'BTC': percentage * exposure,
    'ETH': percentage * exposure,
    # 'UNI': percentage * exposure,
    # 'VET': percentage * exposure,
    # 'DOT': percentage * exposure,
    # 'SOL': percentage * exposure,
    # 'AAVE': percentage * exposure,
    'BNB': percentage * exposure,
    # 'NANO': percentage * exposure,
    # 'MATIC': percentage * exposure,
    # 'XLM': percentage * exposure,
    # 'EOS': percentage * exposure,
    # 'LINK': percentage * exposure,
    # 'ATOM': percentage * exposure,
}


# Percentage of deviation to rebalance. Set to None if want to disable it
# for 1.0 value if asset has 10%, causes rebalancing if it takes >=11% or <=9%
# minimum_percentage_deviation = 1.0 * exposure
minimum_percentage_deviation = None


"""
Fiat asset selected. Use BUSD, USDT, and so on
"""

fiat_asset = 'BUSD'
fiat_decimals = 2
