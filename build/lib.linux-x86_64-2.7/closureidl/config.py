import os as _os
import appdirs as _appdirs
import beaker.cache as _cache
from beaker.util import parse_cache_config_options as _parse_config

version = "0.1.1"

appdirs = _appdirs.AppDirs("closureidl", "closureidl")

_cache_opts = {
  "cache.type": "file",
  "cache.data_dir": _os.path.join(appdirs.user_cache_dir, "data"),
  "cache.lock_dir": _os.path.join(appdirs.user_cache_dir, "lock")
}

def get_cache_mgr(type_="file"):
    _cache_opts["cache.type"] = type_
    opts = _parse_config(_cache_opts)
    return _cache.CacheManager(**opts)
