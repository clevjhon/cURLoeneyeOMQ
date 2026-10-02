import hashlib, os
class OeneyeDBJournal:
    def __init__(self, db_path="oeneye_state.db"):
        self.db_path = db_path
    def commit_transaction(self, payload: bytes):
        h = hashlib.sha256(payload).digest()
        with open(self.db_path, "ab") as fp:
            fp.write(payload)
            fp.write(h)
        os.sync()
