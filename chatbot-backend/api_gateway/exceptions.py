# exceptions.py

class GatewayError(Exception):
    """Base error — all gateway errors inherit this"""
    pass


class AllModelsFailedError(GatewayError):
    """
    Every model in fallback chain failed.
    Means: all keys exhausted, all models down.
    User should see a clean message from this.
    """
    pass


class NoHealthyKeyError(GatewayError):
    """
    A specific model has no healthy keys right now.
    Gateway will try next model in chain.
    """
    pass


class EmptyResponseError(GatewayError):
    """
    Model responded but sent empty text.
    Treated same as a failure — retry next key.
    """
    pass


class ProviderNotFoundError(GatewayError):
    """
    Config has a provider name that doesn't exist.
    Means someone made a typo in config.py
    """
    pass