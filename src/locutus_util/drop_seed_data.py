"""Remove seed data from a specified gcp project.

Jira Issue: FD-1618
"""

from locutus_util.helpers import *
import argparse

# List seed data collections.
seed_collections = ["test_collection"]

# List seed data documents as tuples: (collection_name, document_id) [("","")]
seed_documents = []

def drop_seed_data(args=None):
    """Delete specified collections and documents(seed data) from the specified
    Firestore project.
    Collections and docuements specified will have all sub-files dropped.
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-p', '--project', required=True, help="GCP Project to edit")
    args = parser.parse_args(args)

    # Set the correct project
    update_gcloud_project(args.project)

    # Delete collections and sub-files
    for collection in seed_collections:
        print(f"Attempting to delete collection: {collection}")
        delete_collection(collection)

    # Delete documents and sub-files
    for collection, document_id in seed_documents:
        print(f"Attempting to delete document '{document_id}' from collection '{collection}'")
        delete_document(collection, document_id)


if __name__ == "__main__":
    drop_seed_data()