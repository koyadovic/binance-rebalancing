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

    def __init__(self, last_rebalance_expiration_delta=None, trigger_percentage=None, use_file=True):
        self.last_rebalance_expiration_delta = last_rebalance_expiration_delta
        self.trigger_percentage = trigger_percentage
        self.cls = OnPumpOrDumpRebalancingReferee
        self.use_file = use_file

        empty_state = {'last_rebalance': None, 'prices': {}}

        if self.use_file:
            try:
                with open(self.cls._STATE_FILE, 'rb') as f:
                    self.state = pickle.loads(f.read())
            except FileNotFoundError:
                self.state = empty_state
        else:
            self.state = empty_state

    def should_rebalance(self, current_datetime, prices: dict) -> bool:
        if self.state['last_rebalance'] is None:
            # print(f'> should_rebalance True! last_rebalance does not exist')
            return True
        if self.state['last_rebalance'] + self.last_rebalance_expiration_delta < current_datetime:
            # print(f'> should_rebalance True! last_rebalance is old')
            return True
        for asset, current_price in prices.items():
            past_prices = self.state['prices']
            if asset not in past_prices:
                continue
            past_price = past_prices[asset]
            percentage_change = ((current_price - past_price) / past_price) * 100.0
            if percentage_change > self.trigger_percentage:
                # print(f'> should_rebalance True! percentage_change {percentage_change} > {self.trigger_percentage}')
                return True
            if percentage_change < -self.trigger_percentage:
                # print(f'> should_rebalance True! percentage_change {percentage_change} < {-self.trigger_percentage}')
                return True
        # print(f'> should_rebalance False')
        return False

    def rebalanced(self, current_datetime, prices: dict):
        self.state['last_rebalance'] = current_datetime
        self.state['prices'] = prices
        # print(f'Rebalanced!')
        self._save_state()

    def _save_state(self):
        if self.use_file:
            with open(self.cls._STATE_FILE, 'wb') as f:
                f.write(pickle.dumps(self.state))

    def reset_state(self):
        self.state = {'last_rebalance': None, 'prices': {}}
        self._save_state()
