import math
import os

API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')


"""
Crypto: Percentage
"""

percentage = float(math.floor(100 / 10))


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
