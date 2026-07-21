import importlib
import inspect
import pkgutil


def load(package, parent):

    loaded = []

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):

        module = importlib.import_module(
            f"{package.__name__}.{module_name}"
        )

        for _, cls in inspect.getmembers(module, inspect.isclass):

            if cls is parent:
                continue

            if issubclass(cls, parent):

                loaded.append(cls())

    return loaded