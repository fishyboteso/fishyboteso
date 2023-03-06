"""
no imports from fishy itself here, or anything which depends on fishy
"""
import importlib


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


def install_and_import(package, package_url=None):
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        if package_url is None:
            package_url = package
        pip.main(['install', package_url])
    finally:
        globals()[package] = importlib.import_module(package)