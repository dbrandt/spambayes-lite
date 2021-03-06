#!/usr/bin/env python
from __future__ import print_function
import sys
import argparse

from spambayes_lite.storage import DBDictClassifier, MongoClassifier

def update_output(name, count, length):
    if count % 10 == 0 or count == length:
        print(("\r * %s - %3.1f%%  (%d records/%d)"
               % (name, float(count)/length*100, count, length)), end="")
        sys.stdout.flush()

def import_dbm(dbfname, dbname=None, write=False):
    if dbname is None:
        dbname = dbfname.split("/")[-1].split(".")[0]
    old = DBDictClassifier(dbfname, mode="r")
    state = old.db.get("saved state", [0,0,0])
    length = len(old.db)
    count = 0
    if length == 0 or (state[1] == 0 and state[2] == 0):
        print(" ! %s has no records, skipping..." % (dbfname,), end="")
        return
    if write:
        new = MongoClassifier(collection_name=dbname)
        new._set_save_state(state)
        for key, data in old.db.iteritems():
            count += 1
            if key == "saved state":
                continue
            update_output(dbname, count, length)
            new._set_row(key, data[0], data[1])
    else:
        print((" * %s: %d records (spamcount: %d, hamcount: %d -> import target: %s" %
               (dbfname, length, state[2], state[1], dbname)), end="")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert SpamBayes dbm files to MongoDB")
    parser.add_argument("-w", "--write", action="store_true", default=False,
                        help="Write to new database.")
    parser.add_argument("dbfiles", nargs="+", metavar="FILE", help=".dbm files")
    args = parser.parse_args()

    for fname in args.dbfiles:
        import_dbm(fname, write=args.write)
        print()


