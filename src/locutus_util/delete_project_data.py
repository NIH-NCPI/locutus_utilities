"""Remove seed data from a specified gcp project. Move to new branch/PR

Jira Issue: FD-1618
"""

import argparse
import logging
import sys
from datetime import datetime
from google.cloud import firestore
from locutus_util.common import LOGS_PATH
from locutus_util.helpers import (update_gcloud_project, delete_collection,
                                  set_logging_config)

def drop_collection_data(db):
    """Loop through all collections in Firestore and delete them."""
    # Get all top-level collections
    collections = db.collections()
    has_collections = False

    for collection in collections:
        has_collections = True
        logging.info(f"Deleting collection '{collection.id}'...")
        delete_collection(collection)
        
        # After attempting to delete, verify if the collection is empty
        if is_collection_empty(db, collection):
            logging.info(f"Collection '{collection.id}' successfully deleted.")
        else:
            logging.warning(f"Collection '{collection.id}' and its subcollections are not completely deleted.")
            sys.exit(1)

    if not has_collections:
        logging.info("No collections found. Firestore database is already empty.")

def is_collection_empty(db, coll_ref):
    """Check if a collection and its subcollections are empty."""
    # Check for any remaining documents in the collection
    docs = list(coll_ref.limit(1).stream())
    if len(docs) > 0:
        return False

    # Check for any subcollections within the documents of this collection
    for doc in coll_ref.list_documents():
        for subcollection in doc.collections():
            subcoll_ref = db.collection(f"{coll_ref.id}/{doc.id}/{subcollection.id}")
            if not is_collection_empty(subcoll_ref):
                return False

    return True

def delete_project_data(project_id):
    """Delete specified collections and documents(seed data) from the specified
    Firestore project.
    Collections and docuements specified will have all sub-files dropped.
    """
    _log_file = f"{LOGS_PATH}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}_delete_project_data.log"

    # Set logging configs -log file created in data/logs
    set_logging_config(log_file = _log_file)

    # Set the correct project
    update_gcloud_project(project_id)

    # Firestore client after setting the project_id
    db = firestore.Client()

    # Loops through Collections. Deletes Collections/Documents/SubCollections/Documents
    drop_collection_data(db)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Delete Firestore collections and their contents.")
    parser.add_argument('-p', '--project_id', required=True, help="GCP Project to edit")

    args = parser.parse_args()

    delete_project_data(project_id=args.project_id)