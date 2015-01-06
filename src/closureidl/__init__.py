from __future__ import print_function
import os as _os
import sys as _sys
import threading as _threading
import argparse as _argparse
import requests as _requests
from urlparse import urlparse as _urlparse

from .lib.dart import idlparser as _idlparser
from .lib.dart.idlparser import IDLParser as _IDLParser
from .lib.dart.idlnode import IDLFile as _IDLFile

from .config import get_cache_mgr as _get_cache_mgr

from httplib import (
  OK as _HTTP_OK,
  NOT_MODIFIED as _HTTP_NOT_MODIFIED
)

from itertools import (
  imap as _imap,
  izip as _izip,
  chain as _chain
)

try:
    from collections import OrderedDict as _OrderedDict
except ImportError:
    from ordereddict import OrderedDict as _OrderedDict

from .externs import format_file as _format_file

from .config import version as _version


__version__ = _version


def _get_parser(syntax):
    context = _threading.local()
    key = "closureidl_parser_%d"%syntax
    try:
        return context.__getattribute__(key)
    except AttributeError:
        context.__setattr__(key, _IDLParser(syntax=syntax))
        return context.__getattribute__(key)

def _get_http_resource(cache, url):
    try:
        etag = cache.get("key")
    except KeyError:
        etag = None
        
    if etag is None:
        resp = _requests.get(url)
    else:
        resp = _requests.get(url, headers = {
          "If-None-Match": etag
        })
        
    if resp.status_code == _HTTP_NOT_MODIFIED:
        return (True, None)
    elif resp.status_code == _HTTP_OK:
        if etag is not None:
            cache.clear()
        if "etag" in resp.headers:
            cache.put("key", resp.headers["etag"])
        return (False, resp.content)
    else:
        raise RuntimeError("Error: "+resp.status_code)
    
def _get_local_resource(cache, url):
    s_url = _urlparse(url)
    assert s_url.scheme == "file"
    path = s_url.path
    
    try:
        cached_mtime = cache.get("key")
    except KeyError:
        cached_mtime = None
    mtime = _os.stat(path).st_mtime

    if cached_mtime == mtime:
        return (True, None)
    else:
        cache.put("key", mtime)
        with open(path, "r") as fp:
            return (False, fp.read())
        
    
def _path_to_url(url):
    return _urlparse(url, scheme="file").geturl()
    
def get_tree(url, use_cache=True, syntax=_idlparser.WEBKIT_SYNTAX):
    s_url = _urlparse(url)
    
    if s_url.scheme in ["http", "https"]:
        method = _get_http_resource
    elif s_url.scheme == "file":
        method = _get_local_resource
    elif s_url.scheme == "":
        url = _path_to_url(_os.path.abspath(url))
        method = _get_local_resource
    else:
        raise RuntimeError("Protocol unknown: "+s_url.scheme)
    
    cache_mgr = _get_cache_mgr("file" if use_cache else "memory")
    cache = cache_mgr.get_cache(url)
    cached, content = method(cache, url)

    print url
    
    if cached:
        return cache.get("tree")
    else:
        tree = _get_parser(syntax).parse(content)
        if cache.has_key("key"):
            cache.put("tree", tree)
        
        return tree
    
def get_idl_file(tree):
    return _IDLFile(tree)
    
def list_modules(idl_file):
    return (m.id for m in idl_file.modules)

def _iter_uniq(seq):
    seen = set()
    for el in seq:
        if el not in seen:
            yield el

def list_interface_ids(idl_module):
    return _iter_uniq(i.id for i in idl_module.interfaces)

def list_typedef_ids(idl_module):
    return _iter_uniq((t.id, t.type.id) for t in idl_module.typeDefs)

def get_modules_by_ids(idl_file, ids):
    return (m for m in idl_file.modules if m.id in ids)

def get_interfaces(idl_module):
    choices = _OrderedDict()
    for interface in idl_module.interfaces:
        if interface.id in choices:
            choices[interface.id].append(interface)
        else:
            choices[interface.id] = [interface]
    for vals in choices.itervalues():
        if len(vals) == 1:
            yield vals[0]
        else:
            yield vals[-1]

def _print_seq(seq, func, format_func=(lambda a: a)):
    if len(seq) == 1:
            print("\n".join(_imap(format_func, func(seq[0]))))
    else:
        for node in seq:
            it = func(node)
            try:
                els = _imap(format_func,_chain([next(it)], it))
            except StopIteration:
                pass
            else:
                print(node.id+":")
                print("\n".join("\t"+n for n in els))

_syntax = {
  "WEBIDL_SYNTAX": _idlparser.WEBIDL_SYNTAX,
  "WEBKIT_SYNTAX": _idlparser.WEBKIT_SYNTAX,
  "FREMONTCUT_SYNTAX": _idlparser.FREMONTCUT_SYNTAX
}

def main():
    parser = _argparse.ArgumentParser(
      description="Generates Closure Compiler compatible externs "
                  "from IDL files.")
    parser.add_argument("idl_uri", metavar="IDL_URI", 
                        help="IDL file location.")
    
    # modifiers
    parser.add_argument("--nocache", action="store_false", dest="cache",
                        help="Disable caching.")
    
    # actions
    parser.add_argument("--list-modules", action="store_true",
                        help="List modules.")
    parser.add_argument("--list-interfaces", action="store_true",
                        help="List interfaces.")
    parser.add_argument("--list-typedefs", action="store_true",
                        help="List typedefs.")
    
    # parameters
    parser.add_argument("-m", "--module", action="append", dest="modules",
                        metavar="MODULE")
    parser.add_argument("--syntax", default=["WEBIDL_SYNTAX"], nargs=1,
                        choices=_syntax.keys())
    
    args = parser.parse_args()
    
    tree = get_tree(args.idl_uri, use_cache=args.cache, 
                    syntax=_syntax[args.syntax[0]])
    
    idl_file = get_idl_file(tree)
    
    mods = (list(get_modules_by_ids(idl_file, args.modules)) 
            if args.modules is not None else idl_file.modules)
    
    if args.list_modules:
        print("\n".join(list_modules(idl_file)))
    elif args.list_interfaces:
        _print_seq(mods, list_interface_ids)
    elif args.list_typedefs:
        _print_seq(mods, list_typedef_ids, lambda a: " ".join(a))
    else:
        if len(mods) > 1:
            print("Error: Multiple modules. Use --list-modules"
                  " to list available modules, -m to specify.", 
                  file=_sys.stderr)
            return 100
        print(_format_file(args.idl_uri, get_interfaces(mods[0])))
            
    

if __name__ == "__main__":
    _sys.exit(main())
