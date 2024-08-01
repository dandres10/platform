from sqlalchemy.exc import SQLAlchemyError

from src.core.enums.layer import LAYER


""" def execute_transaction(func):
    def wrapper(*args, **kwargs):
        config = kwargs.get("config") or args[1]  # Obtener `config` de kwargs o args
        db = config.db
        try:
            return func(*args, **kwargs)
        except Exception as e:
            method_name = func.__name__
            return f"An error occurred in method {method_name}"
            return None

    return wrapper """


import json
from functools import wraps


def execute_transaction(layer: LAYER):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                method_name = func.__name__
                instance = args[0] if args else None
                class_name = instance.__class__.__name__ if instance else "Unknown"
                try:
                    kwargs_json = json.dumps(
                        {
                            key: (
                                value.to_dict()
                                if hasattr(value, "to_dict")
                                else str(value)
                            )
                            for key, value in kwargs.items()
                        },
                        indent=4,
                    )

                except TypeError:
                    kwargs_json = "Error serializing arguments to JSON"
                    print(kwargs_json)
                    return None

                print(
                    json.dumps(
                        {
                            "layer": f"{layer}",
                            "class_name": f"{class_name}",
                            "method_name": f"{method_name}",
                            "error": f"{e}",
                        },
                        indent=4,
                    )
                )
                return None

        return wrapper

    return decorator
