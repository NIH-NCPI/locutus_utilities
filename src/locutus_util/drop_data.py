"""Remove seed data from a specified gcp project. Move to new branch/PR

Jira Issue: FD-1618
"""

import argparse
import logging
import sys
from google.cloud import firestore
from locutus_util.common import LOGGING_FORMAT
from locutus_util.helpers import update_gcloud_project, delete_collection


logging.basicConfig(
    level=logging.INFO,
    format=LOGGING_FORMAT
)

db = firestore.Client()

def delete_project_data():
    """Loop through all collections in Firestore and delete them."""
    # Get all top-level collections
    # collections = db.collections()
    collections = ['test_collection','test_collection2']

    for collection in collections:
        logging.info(f"Deleting collection '{collection}'...")
        coll_ref = db.collection(collection)
        delete_collection(coll_ref)

    # After attempting to delete, verify if the collection is empty
    if is_collection_empty(coll_ref):
        logging.info(f"Collection '{collection}' successfully deleted.")
    else:
        logging.warning(f"Collection '{collection}' and all subcollections are not deleted.")
        sys.exit(1)

def is_collection_empty(coll_ref):
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

def drop_data(project_id):
    """Delete specified collections and documents(seed data) from the specified
    Firestore project.
    Collections and docuements specified will have all sub-files dropped.
    """
    
    # Set the correct project
    update_gcloud_project(project_id)

    # Loops through Collections. Deletes Collections/Documents/SubCollections/Documents
    delete_project_data()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Delete Firestore collections and their contents.")
    parser.add_argument('-p', '--project', required=True, help="GCP Project to edit")

    args = parser.parse_args()

    drop_data(project_id=args.project)