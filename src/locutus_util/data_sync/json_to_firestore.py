#!/usr/bin/env python3
"""
JSON to Firestore Import Script

This script imports data from a JSON file into Firestore.
The JSON file should have a structure where top-level keys are collection names,
and their values are dictionaries mapping document IDs to document data.
This format is compatible with the output of firestore_to_json.py.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import argparse
import logging
import sys
from typing import Dict, List, Any, Optional
from google.cloud import firestore_v1
from google.oauth2 import service_account

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FirestoreImporter:
    def __init__(self, project_id: Optional[str] = None, credentials_path: Optional[str] = None, database: Optional[str] = None):
        """
        Initialize Firestore client
        
        Args:
            project_id: GCP Project ID to connect to
            credentials_path: Path to service account key JSON file (optional)
            database: Firestore database name (uses default if not specified)
        """
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.database = database
        self.db = None
        self.client = None
    
    def connect(self):
        """Connect to Firestore using native Google Cloud Firestore client"""
        try:
            # Initialize credentials
            if self.credentials_path and os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = firestore_v1.Client(
                    project=self.project_id,
                    credentials=credentials,
                    database=self.database
                )
            else:
                # Use default credentials with specified project and database
                self.client = firestore_v1.Client(
                    project=self.project_id,
                    database=self.database
                )
            
            # Store reference to database 
            self.db = self.client
            
            database_info = f" (using database: {self.database})" if self.database else " (using default database)"
            logger.info(f"Connected to Firestore project: {self.project_id or 'default'}{database_info}")
        except Exception as e:
            logger.error(f"Failed to connect to Firestore: {e}")
            raise

    def disconnect(self):
        """Disconnect from Firestore"""
        # No need to explicitly close the client
        logger.info("Disconnected from Firestore")
    
    def import_json_file(self, file_path: str, collections_to_import: Optional[List[str]] = None) -> bool:
        """
        Import data from a JSON file into Firestore
        
        Args:
            file_path: Path to the JSON file
            collections_to_import: Optional list of collections to import; if None, all collections are imported
        
        Returns:
            True if the import was successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"JSON file not found: {file_path}")
                return False
            
            # Load JSON data
            logger.info(f"Loading data from {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if not isinstance(json_data, dict):
                logger.error(f"Expected JSON object with collection names as keys, got {type(json_data)}")
                return False
            
            # Filter collections if needed
            if collections_to_import:
                collections = {k: v for k, v in json_data.items() if k in collections_to_import}
                logger.info(f"Filtered {len(collections)}/{len(json_data)} collections based on provided list")
            else:
                collections = json_data
            
            logger.info(f"Found {len(collections)} collections to import")
            
            total_documents = 0
            total_errors = 0
            
            # Process each collection
            for collection_name, documents in collections.items():
                if not isinstance(documents, dict):
                    logger.error(f"Expected documents object for collection {collection_name}, got {type(documents)}")
                    continue
                
                logger.info(f"Importing {len(documents)} documents into collection: {collection_name}")
                
                # Get collection reference using the native client
                collection_ref = self.client.collection(collection_name)
                
                # Import documents
                success_count = 0
                for doc_id, doc_data in documents.items():
                    try:
                        # Use document ID from the JSON structure
                        collection_ref.document(doc_id).set(doc_data)
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Error importing document {doc_id} to {collection_name}: {e}")
                        total_errors += 1
                
                total_documents += success_count
                logger.info(f"Successfully imported {success_count}/{len(documents)} documents to {collection_name}")
            
            logger.info(f"Import complete: {total_documents} documents imported with {total_errors} errors")
            return total_errors == 0
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False
    



def main():
    """Main function to execute the JSON to Firestore import"""
    parser = argparse.ArgumentParser(
        description="Import JSON data into Firestore"
    )
    parser.add_argument(
        'json_file',
        help="Path to the JSON file to import"
    )
    parser.add_argument(
        '-p', '--project-id',
        help="GCP Project ID to connect to (uses default if not specified)"
    )
    parser.add_argument(
        '-k', '--key-file',
        help="Path to service account key JSON file (uses default credentials if not specified)"
    )
    parser.add_argument(
        '-c', '--collections',
        nargs='+',
        help="Optional list of collections to import (imports all if not specified)"
    )
    parser.add_argument(
        '-d', '--database',
        help="Firestore database name (uses default database if not specified)"
    )
    
    args = parser.parse_args()
    
    # Initialize the importer
    importer = FirestoreImporter(
        project_id=args.project_id,
        credentials_path=args.key_file,
        database=args.database
    )
    
    try:
        # Connect to Firestore
        importer.connect()
        
        # Import data
        success = importer.import_json_file(args.json_file, args.collections)
        
        if success:
            logger.info("Import completed successfully")
        else:
            logger.error("Import completed with errors")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)
    finally:
        # Make sure to disconnect
        importer.disconnect()


if __name__ == "__main__":
    main()

"""
Example usage:
python json_to_firestore.py firestore_backup.json -p mapdragon-unified
python json_to_firestore.py firestore_backup.json -p mapdragon-unified  -d loc-mongo
"""

if __name__ == '__main__':
    main()
