import math
import os

API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')


"""
Fiat asset selected. Use BUSD, USDT, and so on
"""

fiat_asset = 'BUSD'
fiat_decimals = 2

"""
Crypto: Percentage
"""

percentage = float(math.floor(100 / 10))

# leaving a tiny piece of fiat untouched
exposure = 0.99  # Recommended max 0.99, min 0.01

portfolio_setting = {
    'ADA': percentage * exposure,
    'ETH': percentage * exposure,
    'UNI': percentage * exposure,
    'VET': percentage * exposure,
    'DOT': percentage * exposure,
    'SOL': percentage * exposure,
    'AAVE': percentage * exposure,
    'BNB': percentage * exposure,
    'NANO': percentage * exposure,
    'MATIC': percentage * exposure,
    # 'XLM': percentage * exposure,
    # 'EOS': percentage * exposure,
    # 'LINK': percentage * exposure,
    # 'ATOM': percentage * exposure,
}


# Percentage of deviation to rebalance. Set to None if want to disable it
minimum_percentage_deviation = 1.0  # for 1.0 value if asset has 10%, causes rebalancing if it takes >=11% or <=9%
