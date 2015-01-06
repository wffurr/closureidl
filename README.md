closureidl
==========

Closure externs generator for WebIDL.

Forked from https://code.google.com/p/closureidl/ at version 0.1.1.

Adds support for WebIDL enum definitions.

```
usage: closureidl [-h] [--nocache] [--list-modules] [--list-interfaces]
                  [--list-typedefs] [-m MODULE]
                  [--syntax {FREMONTCUT_SYNTAX,WEBKIT_SYNTAX,WEBIDL_SYNTAX}]
                  IDL_URI

Generates Closure Compiler compatible externs from IDL files.

positional arguments:
  IDL_URI               IDL file location.

optional arguments:
  -h, --help            show this help message and exit
  --nocache             Disable caching.
  --list-modules        List modules.
  --list-interfaces     List interfaces.
  --list-typedefs       List typedefs.
  -m MODULE, --module MODULE
  --syntax {FREMONTCUT_SYNTAX,WEBKIT_SYNTAX,WEBIDL_SYNTAX}
```
