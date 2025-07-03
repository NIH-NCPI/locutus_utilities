
_db_client = None 

def init_database(mongo_uri=None):
    """Initialize the database, leave mongo_uri as None to use a traditional firestore connection"""

    if _db_client is None:
        if mongo_uri:
            from locutus.storage.mongo import persistence

        else:
            from locutus.storage.firestore import persistence

        _db_client = persistence(mongo_uri)

    return _db_client 
