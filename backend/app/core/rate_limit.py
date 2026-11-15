"""One limiter shared by middleware and route decorators."""
from unittest.mock import patch

import slowapi.extension as _slowapi_ext
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.config import Config


class _SafeConfig(Config):
    """Config that never reads from disk, avoiding cp1252 file decode errors."""

    def __init__(self, *args, **kwargs):
        super().__init__(env_file=None)


# Build the Limiter without letting slowapi attempt to open any .env file with cp1252.
# By patching slowapi's isfile lookup and Config constructor, slowapi initializes Config(None),
# which reads directly from process environment variables without disk I/O.
with patch.object(_slowapi_ext.os.path, "isfile", return_value=False), \
     patch.object(_slowapi_ext, "Config", _SafeConfig):
    limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
