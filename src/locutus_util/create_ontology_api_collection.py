"""
Uses the ontology_definition.csv to create a document for each API 
in the 'OntologyAPI' firestore collection.

Jira ticket FD-1382s
"""

import csv
from google.cloud import firestore
import sys
import os

# Specify the path to resources
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from locutus_util.resources import ONTOLOGY_API_LOOKUP_TABLE_PATH

# Initialize Firestore client
db = firestore.Client()

# Inserts data as a document into the specified collection
def add_ontology_api(api_id, api_url, ontologies):
    # References a collection
    collection_title = 'OntologyAPI'
    ontology_api_ref = db.collection(collection_title)

    # Set the document_id
    document_id = api_id
    
    # Data to store
    data = {
        'api_id': api_id,
        'api_url': api_url,
        'ontologies': ontologies
    }


    # Add a new document to the collection
    # Adding a doc will create a collection if it does not already exist
    ontology_api_ref.document(document_id).set(data)

    print(f"Created {document_id} document in the {collection_title} collection")

def populate_ontology_api_from_csv(csv_file_path):
    api_data = {}

    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            
            # identify individual apis
            api_id = row['api_id']
            if api_id not in api_data:
                api_data[api_id] = {
                    'api_url': row['api_url'],
                    'ontologies': {}
                }

            # Insert ontology details into the correct api dictionary
            ontology_id = row['ontology_code']
            api_data[api_id]['ontologies'][ontology_id] = {
                'ontology_title': row['ontology_title'],
                'ontology_code': row['ontology_code'],
                'curie': row['curie'],
                'system': row['system'],
                'version': row['version'],
            }

    for api_id, data in api_data.items():
        add_ontology_api(api_id, data['api_url'], data['ontologies'])


# Create a document for each api in the OntologyAPI collection
populate_ontology_api_from_csv(ONTOLOGY_API_LOOKUP_TABLE_PATH)

