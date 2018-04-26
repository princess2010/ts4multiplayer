from functools import wraps


def inject(target_object, target_function_name):
    def _wrap_original_function(original_function, new_function):
        @wraps(original_function)
        def _wrapped_function(*args, **kwargs):
            return new_function(original_function, *args, **kwargs)

        return _wrapped_function

    def _injected(wrap_function):
        original_function = getattr(target_object, target_function_name)
        setattr(target_object, target_function_name, _wrap_original_function(original_function, wrap_function))
        return wrap_function

    return _injected
