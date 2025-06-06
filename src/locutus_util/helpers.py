import subprocess
import logging
import sys
import time
import subprocess
import pandas as pd
from pathlib import Path
from google.cloud import firestore
from googleapiclient.discovery import build
from locutus_util.common import (COL_TIME_LIMIT,SUB_TIME_LIMIT,BATCH_SIZE,LOCUTUS_SYSTEM_MAP_PATH)

logger = logging.getLogger(__name__)

def set_logging_config(log_file):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

# Initialize Firestore client
db = firestore.Client()

def update_gcloud_project(project_id):
    """Update the active Google Cloud project."""
    command = ["gcloud", "config", "set", "project", project_id]
    
    try:
        logging.info(f"Updating Google Cloud project to: {project_id}")
        subprocess.run(command, check=True)
        logging.info(f"Project updated successfully: {project_id}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error updating project: {e}")


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

def delete_collection(coll_ref, batch_size=BATCH_SIZE, time_limit=COL_TIME_LIMIT):
    """
    Delete all documents in a collection, handling batches and subcollections.
    Includes a time limit to prevent infinite running.

    Args:
        coll_ref (CollectionReference): The Firestore collection reference.
        batch_size (int): The number of documents to delete per batch.
        time_limit (int): Maximum time in seconds to spend on deletion before stopping.
    """
    start_time = time.time()
    while True:
        # Checks the time limit has not expired
        if time.time() - start_time > time_limit:
            logging.warning(f"Timeout reached while deleting collection '{coll_ref.id}'. Stopping.")
            break
        
        # Gets document_ids from the collection reference
        docs = coll_ref.list_documents(page_size=batch_size)

        deleted = 0

        # Recursively delete any subcollections of the document
        for doc in docs:
            try:
                delete_subcollections(doc)  
                logging.info(f"Deleting document {doc.id} from collection '{coll_ref.id}'.")
                doc.delete()
                deleted += 1
            except Exception as e:
                logging.error(f"Failed to delete document {doc.id}: {e}")

        if deleted == 0:
            logging.info(f"No more documents to delete in collection '{coll_ref.id}'.")
            break

        logging.info(f"Deleted {deleted} documents from collection '{coll_ref.id}'.")

        # Continue if the number of deleted documents reached the batch size, otherwise stop
        if deleted < batch_size:
            break

def delete_subcollections(doc_ref, batch_size=BATCH_SIZE, time_limit=SUB_TIME_LIMIT):
    """
    Delete all subcollections of a given document, with a time limit to prevent infinite run
    
    Args:
        doc_ref (DocumentReference): The Firestore document reference.
        batch_size (int): The number of documents to delete per batch.
        time_limit (int): Maximum time in seconds to spend on deleting subcollections.
    """
    start_time = time.time()
    for subcollection in doc_ref.collections():
        if time.time() - start_time > time_limit:
            logging.warning(f"Timeout reached while deleting subcollections for document '{doc_ref.id}'. Stopping.")
            break

        logging.info(f"Deleting subcollection '{subcollection.id}' for document '{doc_ref.id}'.")
        delete_collection(subcollection, batch_size=batch_size, time_limit=time_limit)

def write_file(filepath, data, sort_by_list=[]):
    """Creates a directory for the table and writes a YAML, SQL, BASH, or Markdown file based on the extension."""
    filepath = Path(filepath)
    file_extension = filepath.suffix

    data = pd.DataFrame(data)
    data = data.sort_values(by=sort_by_list)

    file_handlers = {
        ".csv": lambda: data.to_csv(filepath, index=False),
        ".tsv": lambda: data.to_csv(filepath, sep='\t', index=False)
    }

    if file_extension not in file_handlers:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    logging.debug(f"Writing {file_extension} to file: {filepath}")
    file_handlers[file_extension]()

    logging.info(f"Generated: {Path(filepath).name}")

def load_ontology_lookup():
    df = pd.read_csv(LOCUTUS_SYSTEM_MAP_PATH)
    return dict(zip(df["curie"], df["system"]))

def import_google_sheet(sheet_id, tab_id, output_filepath=None, sort_by_list=None):
    """
    Imports a Google Sheet tab as a Pandas DataFrame using authenticated access
    and optionally writes it to a local file.

    Args:
        sheet_id (str): Google Sheet ID.
        tab_id (str): GID (tab ID).
        output_filepath (str, optional): If given, will save the file to this path.
        sort_by_list (list[str], optional): If saving, sort the output by these columns.

    Returns:
        pd.DataFrame: The data from the Google Sheet.
    """
    service = build('sheets', 'v4')

    # Convert the tab_id (gid) into an A1 notation range (assume full sheet for now)
    range_name = f"'{tab_id}'"  # tab_id must be the sheet name (NOT numeric gid)

    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range=range_name
        ).execute()

        rows = result.get('values', [])
        if not rows:
            logging.warning("No data found in the sheet.")
            return pd.DataFrame()
        
        df = pd.DataFrame(rows[1:], columns=rows[0])

        if output_filepath:
            write_file(output_filepath, df)

        return df

    except Exception as e:
        logging.error(f"Error accessing Google Sheet: {e}")
        raise


def login_with_scopes():
    """
    Runs gcloud command to log in with both Firestore and Google Sheets scopes.
    TODO: Possibly use GOOGLE AUTHENTICATION CREDENTIALS with a service account to auth
    """
    firestore_scope = "https://www.googleapis.com/auth/datastore"
    sheets_scope = " https://www.googleapis.com/auth/spreadsheets.readonly,https://www.googleapis.com/auth/drive.readonly"
    scopes = ",".join([firestore_scope, sheets_scope])

    try:
        print("Logging in with Firestore and Sheets scopes...")
        subprocess.run(
            ["gcloud", "auth", "application-default", "login", f"--scopes={scopes}"],
            check=True
        )
        print("Logged in with combined scopes.")
    except subprocess.CalledProcessError as e:
        print(f"Login failed: {e}")
