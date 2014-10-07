import sys

from pymongo import MongoClient

from .Options import options
from .classifier import Classifier

class MongoClassifier(object, Classifier):
    """Classifier with state persisted in MongoDB."""

    def __init__(self, db_url="mongodb://localhost", db_name="spambayes_lite",
                 collection_name="spambayes"):
        classifier.Classifier.__init__(self)
        self.collection_name = collection_name
        self.db_name = db_name
        self.db_url = db_url
        self.load()

    def load(self):
        """Load this instance from the latest collection."""
        # SpamBayes insists of storing the complete state in a pickle or
        # Shelve or other database, I'd solve it differently, but for now
        # I'm following along.
        if options["globals", "verbose"]:
            print("Loading state from MongoDB (%s, %s)" % (self.db_name, self.db_url),
                  file=sys.stderr)

        try:
            self.db = pymongo.MongoClient(self.db_url)[self.db_name]
        except:
            import pdb; pdb.set_trace()

        if self.collection_name in self.db.collection_names():

            classifier.Classifier.__setstate__(self,
                                               tempbayes.__getstate__())
            if options["globals", "verbose"]:
                print('%s collection exists, has %d ham and %d spam' %
                      (self.collection_name, self.nham, self.nspam), file=sys.stderr)
        else:
            if options["globals", "verbose"]:
                print("%s is a new collection" % (self.collection_name,),
                      file=sys.stderr)
            self.wordinfo = {}
            self.nham = 0
            self.nspam = 0

    def store(self):
        """Store state as new collection."""
        if options["globals", "verbose"]:
            print("Persisting as a collection %s" % (collection_name,),
                  file=sys.stderr)


    def close(self):
        pass
