from collections import namedtuple

from pymongo import MongoClient
from . import classifier

class MongoClassifier(object, classifier.Classifier):
    """Classifier with state persisted in MongoDB."""

    STATE_COLLECTION = "save_state"

    def __init__(self, db_url="mongodb://localhost", db_name="spambayes_lite",
                 collection_name="spambayes"):
        classifier.Classifier.__init__(self)
        self.collection_name = collection_name
        self.db_name = db_name
        self.db_url = db_url
        self.load()

    def load(self):
        try:
            self.db = MongoClient(self.db_url)[self.db_name]
        except:
            import pdb; pdb.set_trace()


        state = self.db[self.STATE_COLLECTION].find_one(
            {"collection": self.collection_name})
        if state is not None:
            self.wordinfo = state.get("wordinfo", {})
            self.nham = state.get("nham", 0)
            self.nspam = state.get("nspam", 0)
        else:
            # Collection of this type does not exist.
            self.wordinfo = {}
            self.nham = 0
            self.nspam = 0
            self.db.create_collection(self.collection_name)
            self.db[self.STATE_COLLECTION].insert(
                {"collection": self.collection_name,
                 "wordinfo": self.wordinfo,
                 "nspam": self.nspam,
                 "nham": self.nham})
        self.db[self.collection_name].ensure_index("word")

    def __repr__(self):
        return ("MongoClassifier(url=%s, db=%s, collection=%s, nham=%d, nspam=%d)" %
                (self.db_url, self.db_name, self.collection_name, self.nham, self.nspam))

    def close(self):
        self._set_save_state((self.wordinfo, self.nspam, self.nham))

    def _copy_from_base(self, base_collection):
        if base_collection in self.db.collection_names():
            for row in self.db[base_collection].find():
                self.db[self.collection_name].insert(row)
            state = self.db[self.STATE_COLLECTION].find_one(
                {"collection": base_collection}) or {}
            state = (state.get("wordinfo", {}), state.get("nspam", 0), state.get("nham", 0))
            self._set_save_state(state)

    def _get_row(self, word, retclass=dict):
        return self.db[self.collection_name].find_one(
            {"word": word}, as_class=retclass)

    def _set_row(self, word, nspam, nham):
        self.db[self.collection_name].update(
            {"word": word}, {"$set": {"nspam": nspam, "nham": nham}},
            upsert=True)

    def _delete_row(self, word):
        self.db[self.collection_name].remove({"word": word})

    def _has_key(self, key):
        return self.db[self.collection_name].find_one({"word": word}) is not None

    def _wordinfoget(self, word):
        row = self._get_row(word)
        if row is not None:
            wi = classifier.WordInfo()
            wi.__setstate__((row["nspam"], row["nham"]))
            return wi

    def _wordinfoset(self, word, record):
        if isinstance(word, unicode):
            word = word.encode("utf-8")
        self._set_row(word, record.spamcount, record.hamcount)

    def _wordinfodel(self, word):
        if isinstance(word, unicode):
            word = word.encode("utf-8")
        self._delete_row(word)

    def _wordinfokeys(self):
        return [r["word"] for r in self.db[self.collection_name].find()
                if "word" in r]

    def _set_save_state(self, state):
        self.db[self.STATE_COLLECTION].update(
            {"collection": self.collection_name},
            {"$set":
             {"collection": self.collection_name,
              "wordinfo": state[0],
              "nspam": state[1],
              "nham": state[2]}}, upsert=True)
        self.wordinfo = state[0]
        self.nspam = state[1]
        self.nham = state[2]
