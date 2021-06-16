from core.bootstrap import init_core_module
from activity.bootstrap import init_activity_module
from core.domain import services as rebalancing_services

import settings
import sys


def main():
    init_core_module()

    # read activity/README.md
    init_activity_module()

    rebalancing_services.rebalance(
        crypto_assets=settings.crypto_assets,
        fiat_asset=settings.fiat_asset,
        fiat_decimals=settings.fiat_decimals,
        exposure=settings.exposure,
        with_confirmation=len(sys.argv) == 1 or sys.argv[1].lower().strip() not in ['--yes', '-y'],
        distribution=settings.distribution
    )


if __name__ == '__main__':
    main()
