#!/usr/bin/env python3
"""
MongoDB Import Script for Firestore Data

This script imports JSON data exported from Firestore into a MongoDB database.
It maps Firestore collections to MongoDB collections and preserves document IDs.
"""

import json
import pymongo
from pymongo import MongoClient
import logging
import argparse
from typing import Dict, Any
import sys
from pathlib import Path
from collections import defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoImporter:
    def __init__(self, mongo_uri: str = "mongodb://admin:password@localhost:27017/", database_name: str = "locutus"):
        """
        Initialize MongoDB importer
        
        Args:
            mongo_uri: MongoDB connection URI
            database_name: Name of the database to import data into
        """
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.client = None
        self.db = None
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def clear_database(self):
        """Clear all collections in the database (use with caution!)"""
        try:
            collection_names = self.db.list_collection_names()
            for collection_name in collection_names:
                self.db[collection_name].drop()
                logger.info(f"Dropped collection: {collection_name}")
            logger.info("Database cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise
    
    def import_firestore_data(self, json_file_path: str):
        """
        Import Firestore JSON backup into MongoDB
        
        Args:
            json_file_path: Path to the Firestore backup JSON file
        """
        try:
            # Load JSON data
            logger.info(f"Loading data from {json_file_path}")
            with open(json_file_path, 'r', encoding='utf-8') as f:
                firestore_data = json.load(f)
            
            subcollection_ids = set(firestore_data['subcollection_names'])
            md_data = firestore_data['collections']

            logger.info(f"Loaded data with {len(md_data)} collections")
            
            # Import each Firestore collection as a MongoDB collection
            total_documents = 0
            for collection_name, documents in md_data.items():
                logger.info(f"Importing collection: {collection_name}")

                subcollections = defaultdict(dict)
                
                # Get or create MongoDB collection
                mongo_collection = self.db[collection_name]
                
                # Prepare documents for insertion
                docs_to_insert = []
                for doc_id, doc_data in documents.items():
                    for id in subcollection_ids:
                        if id in doc_data:
                            data_chunk = doc_data.pop(id, None)
                            # if data_chunk:
                            #     subcollections[id][doc_id] = data_chunk
                            
                    # Add the original Firestore document ID
                    if isinstance(doc_data, dict):
                        doc_data['_firestore_id'] = doc_id
                        docs_to_insert.append(doc_data)
                    else:
                        # Handle cases where doc_data might not be a dict
                        logger.warning(f"Skipping non-dict document {doc_id} in collection {collection_name}")
                        continue
                
                if docs_to_insert:
                    # Insert all documents at once
                    result = mongo_collection.insert_many(docs_to_insert)
                    logger.info(f"Inserted {len(result.inserted_ids)} documents")
                    
                    total_documents += len(docs_to_insert)
                    logger.info(f"Completed importing {len(docs_to_insert)} documents into {collection_name}")
                    
                    # Create index on _firestore_id for better query performance
                    mongo_collection.create_index("_firestore_id", unique=True)
                    logger.info(f"Created index on _firestore_id for collection {collection_name}")
                else:
                    logger.info(f"No documents to insert for collection {collection_name}")

                # for sid, sdata in subcollections.items():
                    
            
            logger.info(f"Data import completed successfully. Total documents imported: {total_documents}")
            
            # Display summary
            self.display_import_summary()
            
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            raise
    
    def display_import_summary(self):
        """Display a summary of imported data"""
        try:
            logger.info("Import Summary:")
            logger.info("=" * 50)
            
            collection_names = self.db.list_collection_names()
            total_docs = 0
            
            for collection_name in sorted(collection_names):
                count = self.db[collection_name].count_documents({})
                total_docs += count
                logger.info(f"  {collection_name}: {count} documents")
            
            logger.info("=" * 50)
            logger.info(f"Total collections: {len(collection_names)}")
            logger.info(f"Total documents: {total_docs}")
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")


def main():
    """Main function to execute the import"""
    parser = argparse.ArgumentParser(
        description="Import Firestore JSON backup into MongoDB"
    )
    parser.add_argument(
        '--json-file',
        help="Path to the Firestore backup JSON file"
    )
    parser.add_argument(
        '--mongo-uri',
        default="mongodb://admin:password@localhost:27017/",
        help="MongoDB connection URI (default: mongodb://admin:password@localhost:27017/)"
    )
    parser.add_argument(
        '--database',
        default="locutus",
        help="MongoDB database name (default: locutus)"
    )
    parser.add_argument(
        '--clear-database',
        action='store_true',
        help="Clear the database before importing (use with caution!)"
    )
    
    args = parser.parse_args()
    
    # Check if JSON file exists
    json_path = Path(args.json_file)
    if not json_path.exists():
        logger.error(f"JSON file not found: {args.json_file}")
        sys.exit(1)
    
    # Initialize importer
    importer = MongoImporter(
        mongo_uri=args.mongo_uri,
        database_name=args.database
    )
    
    try:
        # Connect to MongoDB
        importer.connect()
        
        # Clear database if requested
        if args.clear_database:
            confirmation = input("Are you sure you want to clear the database? (yes/no): ")
            if confirmation.lower() == 'yes':
                importer.clear_database()
            else:
                logger.info("Database clearing cancelled")
                sys.exit(0)
        
        # Import data
        importer.import_firestore_data(args.json_file)
        
        logger.info("Import process completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Import process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Import process failed: {e}")
        sys.exit(1)
    finally:
        importer.disconnect()


if __name__ == "__main__":
    main()
"""
Example usage: Mapdragon-united mongoDB container must be running
    python json_to_mongo.py --json_file firestore_backup.json \
    --mongo-uri mongodb://admin:password@localhost:27017 \
    --database locutus --clear-database
"""