# Activity
To automatically get logs for crypto balances and total fiat balance of your account, initialize the module at startup as this:

```
from activity.bootstrap import init_activity_module

init_activity_module()
```

It will compile the events `crypto-asset-balance` and `total-balance` emitted from `core` module.
