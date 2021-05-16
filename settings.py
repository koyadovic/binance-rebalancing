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

percentage = float(math.floor(100 / 14)) - 0.05  # leaving a tiny piece of fiat untouched

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
    'UNI': percentage,
    'XLM': percentage,
    'LINK': percentage,
    'ATOM': percentage,
}
