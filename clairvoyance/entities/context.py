import logging
from contextvars import ContextVar
from typing import Callable

from clairvoyance.entities.interfaces import IClient, IConfig

config_ctx: ContextVar[IConfig] = ContextVar('config')
client_ctx: ContextVar[IClient] = ContextVar('client')
logger_ctx: ContextVar[logging.Logger] = ContextVar('logger')

# Get the logger.
logger = logging.getLogger()

# Add a file handler to the logger.
fh = logging.FileHandler('log.txt')
# Add a stream handler to the logger.
sh = logging.StreamHandler()

# Set the log levels
fh.setLevel(logging.DEBUG)
sh.setLevel(logging.DEBUG)  

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh.setFormatter(formatter)
sh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(sh)

logger.setLevel(logging.DEBUG)

# Quick resolve the context variables using macros.
config: Callable[..., IConfig] = lambda: config_ctx.get()  # pylint: disable=unnecessary-lambda
client: Callable[..., IClient] = lambda: client_ctx.get()  # pylint: disable=unnecessary-lambda
log: Callable[..., logging.Logger] = lambda: logger_ctx.get()  # pylint: disable=unnecessary-lambda
