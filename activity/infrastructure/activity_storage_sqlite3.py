from activity.domain.entities import TotalBalance, CryptoAssetBalance
from activity.domain.interfaces import AbstractActivityStorage
import sqlite3


class SQLite3ActivityStorage(AbstractActivityStorage):
    def __init__(self):
        self._init()

    def save_crypto_asset_balance(self, crypto_asset_balance: CryptoAssetBalance):
        c = self._cursor()
        c.execute(
            'INSERT INTO crypto_asset_balances (timestamp, asset, balance) '
            'VALUES (?, ?, ?);',
            (
                crypto_asset_balance.timestamp.strftime('%Y-%m-%d %H:%M:%S %z'),
                crypto_asset_balance.asset,
                crypto_asset_balance.balance,
            )
        )
        crypto_asset_balance.id = c.lastrowid
        c.close()

    def save_total_balance(self, total_balance: TotalBalance):
        c = self._cursor()
        c.execute(
            'INSERT INTO total_balances (timestamp, fiat_asset, total_balance) '
            'VALUES (?, ?, ?);',
            (
                total_balance.timestamp.strftime('%Y-%m-%d %H:%M:%S %z'),
                total_balance.fiat_asset,
                total_balance.total_balance,
            )
        )
        total_balance.id = c.lastrowid
        c.close()

    """"""

    def _init(self):
        if not self._table_exists('crypto_asset_balances'):
            self._create_table(
                'crypto_asset_balances',
                '''
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    asset TEXT,
                    balance REAL
                )
                '''
            )
        if not self._table_exists('total_balances'):
            self._create_table(
                'total_balances',
                '''
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    fiat_asset TEXT,
                    total_balance REAL
                )
                '''
            )

    def _table_exists(self, table_name):
        c = self._cursor()
        c.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=?;', (table_name,))
        exists = c.fetchone() is not None
        c.close()
        return exists

    def _create_table(self, table_name, structure):
        c = self._cursor()
        sentence = 'CREATE TABLE {table_name} {structure};'.format(table_name=table_name, structure=structure)
        c.execute(sentence)
        c.close()

    def _cursor(self):
        return self._get_conn().cursor()

    def _get_conn(self):
        conn = sqlite3.connect(f'activity.db', isolation_level=None)
        return conn
