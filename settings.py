import math
import os

API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')


"""
Fiat asset selected. Use BUSD, USDT, and so on
"""

fiat_asset = 'USDT'

"""
Crypto: Percentage
"""

percentage = float(math.floor(100 / 10)) - 0.1  # leaving a tiny piece of fiat untouched, a 1%

portfolio_setting = {
    'ADA': percentage,
    'ETH': percentage,
    'EOS': percentage,
    'VET': percentage,
    'DOT': percentage,
    'SOL': percentage,
    'AAVE': percentage,
    'BNB': percentage,
    'NANO': percentage,
    'MATIC': percentage,
}
