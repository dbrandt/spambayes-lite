"""Wrapper to open an appropriate dbm storage type."""

from Options import options
import sys

class error(Exception):
    pass

def open_db3hash(*args):
    """Open a bsddb3 hash."""
    import bsddb3
    return bsddb3.hashopen(*args)

def open_dbhash(*args):
    """Open a bsddb hash.  Don't use this on Windows."""
    import bsddb
    return bsddb.hashopen(*args)

def open_gdbm(*args):
    """Open a gdbm database."""
    import gdbm
    return gdbm.open(*args)

def open_dumbdbm(*args):
    """Open a dumbdbm database."""
    import dumbdbm
    return dumbdbm.open(*args)

def open_best(*args):
    if sys.platform == "win32":
        funcs = [open_db3hash, open_gdbm, open_dumbdbm]
    else:
        funcs = [open_db3hash, open_dbhash, open_gdbm, open_dumbdbm]
    for f in funcs:
        try:
            return f(*args)
        except ImportError:
            pass
    raise error("No dbm modules available!")

open_funcs = {
    "best": open_best,
    "db3hash": open_db3hash,
    "dbhash": open_dbhash,
    "gdbm": open_gdbm,
    "dumbdbm": open_dumbdbm,
    }

def open(*args):
    dbm_type = options.dbm_type.lower()
    f = open_funcs.get(dbm_type)
    if not f:
        raise error("Unknown dbm type in options file")
    return f(*args)