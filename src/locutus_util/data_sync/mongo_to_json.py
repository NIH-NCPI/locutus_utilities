#!/usr/bin/env python3
"""
MongoDB to JSON Export Script

This script exports data from a MongoDB database to a JSON file.
It exports all collections in the database or specified collections only.
"""

import json
import pymongo
from pymongo import MongoClient
import logging
import argparse
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path
from bson import ObjectId
import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


class MongoExporter:
    def __init__(self, mongo_uri: str = "mongodb://admin:password@localhost:27017/", database_name: str = "locutus"):
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.client = None
        self.db = None
    
    def connect(self):
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
    
    def get_collection_names(self) -> List[str]:
        """Get list of all collection names in the database"""
        try:
            return self.db.list_collection_names()
        except Exception as e:
            logger.error(f"Error getting collection names: {e}")
            raise
    
    def export_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Export a single collection to a dictionary
        
        Args:
            collection_name: Name of the collection to export
            
        Returns:
            Dictionary with document IDs as keys and document data as values
        """
        try:
            collection = self.db[collection_name]
            documents = collection.find({})
            
            collection_data = {}
            for doc in documents:
                doc_id = str(doc.pop('_id'))
                
                # If there's a Firestore ID, use that as the document ID
                if '_firestore_id' in doc:
                    doc_id = doc.pop('_firestore_id')
                
                collection_data[doc_id] = doc
            
            logger.info(f"Exported {len(collection_data)} documents from collection {collection_name}")
            return collection_data
        except Exception as e:
            logger.error(f"Error exporting collection {collection_name}: {e}")
            return {}
    
    def export_all_data(self, collection_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export all collections to a dictionary
        
        Args:
            collection_filter: Optional list of collection names to export
                              If None, all collections are exported
        
        Returns:
            Dictionary with collection names as keys and collection data as values
        """
        try:
            all_data = {}
            
            collection_names = self.get_collection_names()
            if collection_filter:
                collection_names = [name for name in collection_names if name in collection_filter]
            
            logger.info(f"Found {len(collection_names)} collections to export")
            
            for collection_name in collection_names:
                logger.info(f"Exporting collection: {collection_name}")
                collection_data = self.export_collection(collection_name)
                all_data[collection_name] = collection_data
            
            return all_data
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return {}
    
    def save_to_json(self, data: Dict[str, Any], output_path: str):
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            output_path: Path to save the JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, cls=MongoJSONEncoder)
            logger.info(f"Data saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving data to JSON: {e}")
            raise


def main():
    """Main function to execute the data export"""
    parser = argparse.ArgumentParser(
        description="Export MongoDB data to JSON"
    )
    parser.add_argument(
        '-u', '--mongo-uri',
        default="mongodb://admin:password@localhost:27017/",
        help="MongoDB connection URI"
    )
    parser.add_argument(
        '-d', '--database',
        default="locutus",
        help="MongoDB database name"
    )
    parser.add_argument(
        '-c', '--collections',
        nargs='+',
        help="Optional list of collections to export (exports all if not specified)"
    )
    parser.add_argument(
        '-o', '--output',
        default='mongodb_export.json',
        help="Output JSON file path (default: mongodb_export.json)"
    )
    
    args = parser.parse_args()
    
    # Initialize the exporter
    exporter = MongoExporter(
        mongo_uri=args.mongo_uri,
        database_name=args.database
    )
    
    try:
        # Connect to MongoDB
        exporter.connect()
        
        # Export data
        data = exporter.export_all_data(args.collections)
        
        # Save to JSON file
        exporter.save_to_json(data, args.output)
        
        logger.info("Export completed successfully")
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)
    finally:
        # Make sure to disconnect
        exporter.disconnect()


if __name__ == "__main__":
    main()
