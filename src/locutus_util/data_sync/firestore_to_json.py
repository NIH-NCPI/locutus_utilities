import firebase_admin
from firebase_admin import credentials, firestore
import json
from typing import Dict, List, Any
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirestoreDataPuller:
    def __init__(self, project_id: str = None):
        """
        Initialize Firestore client
        Args:
            project_id: GCP Project ID to connect to
        """
        # Use default credentials (e.g., from environment)
        firebase_admin.initialize_app(options={
            'projectId': project_id
        } if project_id else None)
        
        self.db = firestore.client()
        self.project_id = project_id
        logger.info(f"Connected to Firestore project: {project_id or 'default'}")
    
    def get_all_collections(self) -> List[str]:
        """Get list of all collection names in the database"""
        try:
            collections = self.db.collections()
            return [collection.id for collection in collections]
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return []
    
    def get_collection_data(self, collection_name: str) -> Dict[str, Any]:
        """Get all documents from a specific collection"""
        try:
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            
            collection_data = {}
            for doc in docs:
                collection_data[doc.id] = doc.to_dict()
            
            return collection_data
        except Exception as e:
            logger.error(f"Error getting data from collection {collection_name}: {e}")
            return {}
    
    def pull_all_data(self) -> Dict[str, Any]:
        """Pull all data from all collections in the database"""
        logger.info("Starting to pull all Firestore data...")
        
        all_data = {}
        collections = self.get_all_collections()
        
        logger.info(f"Found {len(collections)} collections: {collections}")
        
        for collection_name in collections:
            logger.info(f"Pulling data from collection: {collection_name}")
            collection_data = self.get_collection_data(collection_name)
            all_data[collection_name] = collection_data
            logger.info(f"Retrieved {len(collection_data)} documents from {collection_name}")
        
        return all_data
    
    def save_to_json(self, data: Dict[str, Any], output_path: str):
        """Save data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Data saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving data to JSON: {e}")

def main():
    """Main function to execute the data pull"""
    parser = argparse.ArgumentParser(
        description="Pull all data from Firestore and save to JSON"
    )
    parser.add_argument(
        '-p', '--project-id', 
        help="GCP Project ID to connect to (uses default if not specified)"
    )
    parser.add_argument(
        '-o', '--output', 
        default='firestore_backup.json',
        help="Output JSON file path (default: firestore_backup.json)"
    )
    
    args = parser.parse_args()
    
    # Initialize the puller with project ID only
    puller = FirestoreDataPuller(
        project_id=args.project_id
    )
    
    # Pull all data
    all_data = puller.pull_all_data()
    
    # Save to JSON file
    puller.save_to_json(all_data, args.output)
    
    logger.info("Firestore data pull completed successfully")
    return all_data

if __name__ == "__main__":
    main()

"""
Example usage:
python firestore_to_json.py -p locutus-dev --output firestore_backup.json
"""