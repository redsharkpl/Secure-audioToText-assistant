def is_rate_limit_error(e: Exception) -> bool:
    try:
        import google.api_core.exceptions
        if isinstance(e, google.api_core.exceptions.ResourceExhausted):
            return True
    except ImportError:
        pass
    error_str = str(e)
    return any(x in error_str for x in ["429", "RESOURCE_EXHAUSTED", "quota exceeded"])
