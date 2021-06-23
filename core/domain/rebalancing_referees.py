import pickle


class AbstractRebalancingReferee:
    def should_rebalance(self, current_datetime, prices: dict) -> bool:
        raise NotImplementedError

    def rebalanced(self, current_datetime, prices: dict) -> None:
        raise NotImplementedError


class OnExecutionRebalancingReferee(AbstractRebalancingReferee):
    def should_rebalance(self, current_datetime, prices: dict) -> bool:
        return True

    def rebalanced(self, current_datetime, prices: dict) -> None:
        pass


class OnPumpOrDumpRebalancingReferee(AbstractRebalancingReferee):
    _STATE_FILE = f'core/domain/.OnPumpOrDumpRebalancingRefereeState.pkl'

    _empty_state = {
        'last_rebalance': None,
        'starting_prices': {},
        'ending_prices': {},
    }

    def __init__(self, last_rebalance_expiration_delta=None, trigger_percentage=None, persistent_state=True):
        self.last_rebalance_expiration_delta = last_rebalance_expiration_delta
        self.trigger_percentage = trigger_percentage
        self.cls = OnPumpOrDumpRebalancingReferee
        self.persistent_state = persistent_state

        if self.persistent_state:
            try:
                with open(self.cls._STATE_FILE, 'rb') as f:
                    self.state = pickle.loads(f.read())
            except FileNotFoundError:
                self.state = self._empty_state
        else:
            self.state = self._empty_state

    def should_rebalance(self, current_datetime, prices: dict) -> bool:
        rebalance = False
        state_changes = False

        for asset, price in prices.items():
            asset_starting_price = self.state['starting_prices'].get(asset, None)
            if asset_starting_price is None:
                # Si no hay precio de comienzo, se establece precio de comienzo
                self.state['starting_prices'][asset] = price
                state_changes = True
            else:
                # Si sí existe precio de comienzo:
                asset_ending_price = self.state['ending_prices'].get(asset, None)
                if asset_ending_price is None:
                    # No existe precio final
                    self.state['ending_prices'][asset] = price
                    state_changes = True
                else:
                    # Sí existe precio final
                    # Por lo que a buscar si el nuevo precio sigue la tendencia que dibuja del starting al ending

                    # Si va más allá, seteamos el nuevo precio como nuevo ending

                    # Si está entremedias, toca ver si el precio actual con respecto al starting supera
                    #   el trigger_percentage

                    # Si se dió la vuelta al contrario que la tendencia que dibujaba starting/ending
                    #   seteamos nuevo comienzo.

                    if (price > asset_ending_price > asset_starting_price) or (asset_starting_price > asset_ending_price > price):
                        self.state['ending_prices'][asset] = price
                        state_changes = True
                    elif (asset_starting_price < price <= asset_ending_price) or (asset_starting_price >= price > asset_ending_price):
                        percentage_change = ((price - asset_starting_price) / asset_starting_price) * 100.0

                        if percentage_change > self.trigger_percentage:
                            rebalance = True
                        if percentage_change < -self.trigger_percentage:
                            rebalance = True

                    elif (price > asset_starting_price > asset_ending_price) or (asset_ending_price > asset_starting_price > price):
                        self.state['starting_prices'][asset] = price
                        self.state['ending_prices'][asset] = None
                        state_changes = True

        if state_changes:
            self._save_state()

        if self.state['last_rebalance'] is None or self.state['last_rebalance'] + \
                self.last_rebalance_expiration_delta < current_datetime:
            rebalance = True

        return rebalance

    def rebalanced(self, current_datetime, prices: dict):
        self.state['last_rebalance'] = current_datetime
        for asset, price in prices.items():
            self.state['starting_prices'][asset] = price
            self.state['ending_prices'][asset] = None
        self._save_state()

    def _save_state(self):
        if self.persistent_state:
            with open(self.cls._STATE_FILE, 'wb') as f:
                f.write(pickle.dumps(self.state))

    def reset_state(self):
        self.state = self._empty_state
        self._save_state()
