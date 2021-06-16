import os

from core.domain.interfaces import AbstractExchange, AbstractUserInterface
from core.infrastructure.exchange_binance import BinanceExchange
from core.infrastructure.user_interface_text import TextUserInterface
from shared.domain.dependencies import dependency_dispatcher


def init_core_module():
    dependency_dispatcher.register_implementation(
        AbstractExchange,
        BinanceExchange(
            api_key=os.environ.get('BINANCE_API_KEY'),
            api_secret=os.environ.get('BINANCE_API_SECRET'),
        )
    )
    dependency_dispatcher.register_implementation(AbstractUserInterface, TextUserInterface())