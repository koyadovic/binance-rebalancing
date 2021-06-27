import os
from core.domain.interfaces import AbstractExchange, AbstractUserInterface
from core.infrastructure.exchange_binance import BinanceExchange
from core.infrastructure.exchange_binance_simulation import BinanceSimulationExchange
from core.infrastructure.user_interface_text import TextUserInterface
from shared.domain.dependencies import dependency_dispatcher
import sentry_sdk


def init_core_module():
    dependency_dispatcher.register_implementation(
        AbstractExchange,
        BinanceExchange(
            api_key=os.environ.get('BINANCE_API_KEY'),
            api_secret=os.environ.get('BINANCE_API_SECRET'),
        )
    )

    sentry_dsn = os.environ.get('SENTRY_DSN', None)
    if sentry_dsn is not None:
        sentry_sdk.init(sentry_dsn, traces_sample_rate=1.0)
    _common_initialization()


def init_core_module_for_simulations():
    dependency_dispatcher.register_implementation(
        AbstractExchange,
        BinanceSimulationExchange(
            api_key=os.environ.get('BINANCE_API_KEY'),
            api_secret=os.environ.get('BINANCE_API_SECRET'),
        )
    )
    _common_initialization()


def _common_initialization():
    dependency_dispatcher.register_implementation(AbstractUserInterface, TextUserInterface())
