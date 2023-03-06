"""
no imports from fishy itself here, or anything which depends on fishy
"""
def singleton_proxy(instance_name):
    def decorator(root_cls):
        if not hasattr(root_cls, instance_name):
            raise AttributeError(f"{instance_name} not found in {root_cls}")

        class SingletonProxy(type):
            def __getattr__(cls, name):
                return getattr(getattr(cls, instance_name), name)

        class NewClass(root_cls, metaclass=SingletonProxy):
            ...

        return NewClass

    return decorator
