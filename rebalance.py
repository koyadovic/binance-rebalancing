import settings
import sys

from shared.domain.dependencies import dependency_dispatcher
from core.domain.interfaces import AbstractExchange, AbstractUserInterface
from core.infrastructure.exchange_binance import BinanceExchange
from core.infrastructure.user_interface_text import TextUserInterface

from core.domain.services import PortfolioRebalancing


def main():
    dependency_dispatcher.register_implementation(
        AbstractExchange,
        BinanceExchange(
            api_key=settings.API_KEY,
            api_secret=settings.API_SECRET,
        )
    )
    dependency_dispatcher.register_implementation(AbstractUserInterface, TextUserInterface())

    portfolio_rebalancing = PortfolioRebalancing()
    portfolio_rebalancing.rebalance(
        crypto_assets=settings.crypto_assets,
        fiat_asset=settings.fiat_asset,
        fiat_decimals=settings.fiat_decimals,
        exposure=settings.exposure,
        with_confirmation=len(sys.argv) == 1 or sys.argv[1].lower().strip() not in ['--yes', '-y'],
    )


if __name__ == '__main__':
    main()
