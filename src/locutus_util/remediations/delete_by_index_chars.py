#!/usr/bin/env python3
import argparse
from google.cloud import firestore
import logging
from datetime import datetime
from locutus_util.common import LOGS_PATH
from locutus_util.helpers import (set_logging_config)

def scan_for_invalid_subcollection_doc_ids(db):
    """
    Scans all documents within subcollections under 'Terminology/*'
    for document IDs containing '/'.
    Returns a list of (terminology_id, subcollection_id, document_id, full_path)
    """
    invalid_ids = []

    term_collection = db.collection('Terminology')

    for term_doc in term_collection.list_documents():
        term_id = term_doc.id
        for subcoll in term_doc.collections():
            subcoll_id = subcoll.id
            for doc in subcoll.list_documents():
                logging.info(f'Scaning Terminology, subcollection: {term_doc.id} / {subcoll.id} / {doc.id}')
                # NOTE: WILL CAPTURE ANY doc id with the character. Use a full match instead, if necessary.
                if "/" in doc.id:
                    invalid_ids.append((
                        term_id,
                        subcoll_id,
                        doc.id,
                        doc.path
                    ))
                    logging.info(f"Invalid ids: {term_doc.id} / {subcoll.id} / {doc.id} - Path to delete: {doc.path}")

    return invalid_ids


def delete_invalid_documents(invalid_ids, db):
    
    for term_id, subcoll_id, id, path in invalid_ids:
        try:
            doc_ref = db.document(path)
            doc_ref.delete()
            logging.info(f"Deleted invalid doc: {term_id} - {subcoll_id} - {id} - {path}")
        except Exception as e:
            logging.error(f"Failed to delete document {path}: {e}")

def main(project_id,database):

    _log_file = f"{LOGS_PATH}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}_remediation.log"

    # Set logging configs -log file created in data/logs
    set_logging_config(log_file = _log_file)

    # Initiate Firestore client and setting the project_id
    db = firestore.Client(project=project_id, database=database)
    
    logging.info("Scanning subcollections under 'Terminology' for bad document IDs...")
    invalid_ids = scan_for_invalid_subcollection_doc_ids(db)

    if not invalid_ids:
        logging.info("No invalid document IDs found.")
        return

    logging.info(f"\nFound {len(invalid_ids)} invalid document IDs. See: {LOGS_PATH}")
    confirm = input("Delete these documents? [y/N]: ").strip().lower()

    if confirm == "y":
        delete_invalid_documents(invalid_ids, db)
    else:
        logging.info("Deletion aborted.")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Delete Terminology documents with slashes in their index.")
    parser.add_argument('-p', '--project_id', required=True, help="GCP Project to edit")
    parser.add_argument('-db', '--database', required=False, help="Database to edit. Will edit the projects default db if not set here.")


    args = parser.parse_args()
    

    main(project_id=args.project_id,database=args.database)
