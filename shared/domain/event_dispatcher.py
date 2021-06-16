from typing import List
import sys
import traceback


class EventDispatcher:

    def __init__(self):
        self.events_listeners = {}
        self._added = {}

    def listen(self, event: str, func, uid_name=None):
        if not callable(func):
            raise TypeError('func argument {} is not callable'.format(func))
        if event not in self.events_listeners:
            self.events_listeners[event] = []
        if event not in self._added:
            self._added[event] = []

        if uid_name is not None:
            if uid_name in self._added[event]:
                return
            else:
                self._added[event].append(uid_name)
        self.events_listeners[event].append({
            'func': func,
        })

    def emit(self, event: str, *args, capture_exceptions=True, **kwargs):
        if event in self.events_listeners:
            listeners = self.events_listeners[event]
            for listener in listeners:
                func = listener['func']
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    if capture_exceptions:
                        traceback.print_exc()
                        exc_info = sys.exc_info()
                        self.emit('uncaught-exception', exception=e, stack=exc_info[2])
                        del exc_info
                    else:
                        raise e

    def listens_on(self, event_name: str, uid_name=None):
        def decorator(func):
            self.listen(event_name, func, uid_name=uid_name)
            return func
        return decorator

    def listens_on_any_of(self, event_names: List[str], uid_name=None):
        def decorator(func):
            for event_name in event_names:
                self.listen(event_name, func, uid_name=uid_name)
            return func
        return decorator


event_dispatcher = EventDispatcher()
