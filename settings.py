import math
import os

API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')


"""
Fiat asset selected. Use BUSD, USDT, and so on
"""

fiat_asset = 'BUSD'

"""
Crypto: Percentage
"""

percentage = float(math.floor(100 / 10)) - 0.1  # leaving a tiny piece of fiat untouched

exposure = 1.0  # max 1.0, min 0.0

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
    # 'LINK': percentage * exposure,
    # 'ATOM': percentage * exposure,
}
