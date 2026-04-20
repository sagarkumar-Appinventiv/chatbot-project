# __init__.py
# Makes llm_gateway importable as a package

from .gateway import call, GatewayResponse
from .key_manager import warmup