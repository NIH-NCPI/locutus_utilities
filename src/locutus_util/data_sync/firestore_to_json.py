import firebase_admin
from firebase_admin import credentials, firestore
import json
from typing import Dict, List, Any
import logging
import argparse
from collections import namedtuple
from locutus import get_code_index

import pdb
import rich 

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
            subcollection_names = set()
            for doc in docs:
                realized_doc = doc.to_dict()

                subcollection_data = {}

                for subcoll in doc.reference.collections():
                    subcollection_names.add(subcoll.id)
                    subcollection_data[subcoll.id] = {}
                    for doc1 in subcoll.stream():
                        subcollection_data[subcoll.id][doc1.id] = doc1.to_dict()

                if len(subcollection_data) > 0:
                    realized_doc["subcollections"] = subcollection_data

                collection_data[doc.id] = realized_doc

            if len(subcollection_names) > 0:
                print(",".join(list(subcollection_names)))
            return subcollection_names, collection_data
        except Exception as e:
            logger.error(f"Error getting data from collection {collection_name}: {e}")
            return {}
        

    def split_terminology_data(self, term_data):
        TerminologyComponents = namedtuple("TerminologyComponents", ['terminologies', 'codes', 'mappings', 'deadcodes', 'deadmappings'])

        def get_subcontainer(terminiology, name):
            if "subcollections" in terminiology:
                return terminiology["subcollections"].get(name)

        terminologies = {}
        mappings = {}
        deadcodes = {}
        deadmappings = {}


        for termid, term in term_data.items():
            # Build out the new Codes collection for each terminology
            code_refs = []

            onto_prefs = get_subcontainer(term, "onto_api_preferences")
            if onto_prefs is not None:
                for code, prefs in onto_prefs.items():
                    if code == "self":
                        term['onto_api_preference'] = prefs 
                    else:
                        codeid = code_id(termid, code)
                        codes[codeid]["onto_api_preference"] = prefs 

            prov = get_subcontainer(term, "provenance")
            if prov is not None:
                for code, prov in prov.items():
                    if code == "self":
                        term['provenance'] = prov 
                    else:
                        codeid = code_id(termid, code)
                        try:
                            codes[codeid]['provenance'] = prov 
                        except:
                            print(f"No code id {codeid}")
                            deadcodes[codeid] = {
                                "code": code,
                                "display": "",
                                "description": "",
                                "provenance": prov
                            }
            
            term_mappings = get_subcontainer(term, "mappings")
            if term_mappings is not None:
                for code, mpp in term_mappings.items():
                    codeid = code_id(termid, code)
                    for mapping in mpp['codes']:
                        mapping_id = f"{codeid}<-{get_code_index(mapping['code'])}"

                        mapping["user_input"] = []
                        mapping['source_code'] = code 
                        mappings[mapping_id] = mapping 

            user_input = get_subcontainer(term, "user_input")
            if user_input is not None: 
                for mppid, uinput in user_input.items():
                    source, mapped = mppid.split("|")

                    codeid = code_id(termid, source)
                    mapping_id = f"{codeid}<-{get_code_index(mapped)}"
                    try:
                        mappings[mapping_id]['user_input'] = uinput
                    except:
                        print(f"No mapping, {mapping_id}, present. ")
                        deadmappings[mapping_id] = {
                            "no_mapping": True,
                            "user_input": uinput
                        }

            terminologies[termid] = term

        return TerminologyComponents(terminologies, codes, mappings, deadcodes, deadmappings)
    
    def pull_all_data(self) -> Dict[str, Any]:
        """Pull all data from all collections in the database"""
        logger.info("Starting to pull all Firestore data...")
        
        all_data = {
            "subcollection_names": [],
            "collections": {}
        }
        collections = self.get_all_collections()
        subcollection_names = set()
        
        logger.info(f"Found {len(collections)} collections: {collections}")
        
        for collection_name in collections:
            logger.info(f"Pulling data from collection: {collection_name}")
            subcolls, collection_data = self.get_collection_data(collection_name)

            """
            if collection_name == "Terminology":
                # termdata = self.split_terminology_data(collection_data)
                subcollection_names.update(subcolls)

                all_data["collections"]["Terminology"] = termdata.terminologies
                all_data['collections']['Code'] = termdata.codes
                all_data['collections']['Mapping'] = termdata.mappings
                all_data['orphans'] = {
                    "codes": termdata.deadcodes,
                    "mappings": termdata.deadmappings
                }
            else:"""
            if True:
                all_data["collections"][collection_name] = collection_data

            logger.info(f"Retrieved {len(collection_data)} documents from {collection_name}")
        all_data["subcollection_names"] = sorted(list(subcollection_names))
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