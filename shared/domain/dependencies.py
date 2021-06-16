class DependencyDispatcher:
    def __init__(self):
        self._dependency_wires = {}

    def register_implementation(self, interface, implementation):
        self._dependency_wires[self._serialize_interface(interface)] = implementation

    def request_implementation(self, interface):
        if type(interface) == str:
            implementation = self._dependency_wires.get(interface, None)
        else:
            implementation = self._dependency_wires.get(self._serialize_interface(interface), None)
        return implementation

    @classmethod
    def _serialize_interface(cls, interface):
        serialized = f'{interface.__module__}.{interface.__name__}'
        return serialized

    def inject(self, serialized_interface):
        def decorator(func):
            def wrapper(*args, **kwargs):
                implementation = self.request_implementation(serialized_interface)
                return func(*args, **kwargs, injected=implementation)
            return wrapper
        return decorator


dependency_dispatcher = DependencyDispatcher()
