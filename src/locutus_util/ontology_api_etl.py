"""This script fetches data from the APIs, combines it with manually 
added ontologies, and then uploads the structured data into Firestore under 
the `OntologyAPI` collection.
"""

import requests
from google.cloud import firestore

# Firestore client
db = firestore.Client()

OLS_API_BASE_URL = "https://www.ebi.ac.uk/ols4/api/"
MONARCH_API_BASE_URL = "https://api-v3.monarchinitiative.org/v3/api/search?q="
LOINC_API_BASE_URL = "https://loinc.regenstrief.org/searchapi/"

ols_ontologies_url = f"{OLS_API_BASE_URL}ontologies"
extracted_data = []

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def collect_ols_data():
    print("Fetching data")
    data = fetch_data(ols_ontologies_url)
    print("Transforming data")

    while data:
        ontologies = data['_embedded']['ontologies']
        for ontology in ontologies:
            config = ontology.get('config', {})
            # Collect ontology data
            extracted_data.append({
                'api_url': OLS_API_BASE_URL,
                'api_id': 'ols',
                'api_name': 'Ontology Lookup Service',
                'ontology_code': ontology['ontologyId'],
                'curie': config.get('preferredPrefix', ''),
                'ontology_title': config.get('title', ''),
                'system': config.get('fileLocation', ''),
                'version': config.get('versionIri', '')
            })
        
        # Check if there is a next page
        if '_links' in data and 'next' in data['_links']:
            next_url = data['_links']['next']['href']
            data = fetch_data(next_url)
        else:
            break

    return extracted_data

def add_manual_ontologies():
    return [
        {
            'api_url': MONARCH_API_BASE_URL,
            'api_id': "monarch",
            'api_name': "Monarch API",
            'ontology_title': "Environmental Conditions, Treatments and Exposures Ontology",
            'ontology_code': "ecto",
            'curie': "ECTO",
            'system': "http://purl.obolibrary.org/obo/ecto.owl",
            'version': ""
        },
        {
            'api_url': LOINC_API_BASE_URL,
            'api_id': "loinc",
            'api_name': "LOINC API",
            'ontology_title': "Logical Observation Identifiers, Names and Codes (LOINC)",
            'ontology_code': "loinc",
            'curie': "",
            'system': "http://loinc.org",
            'version': ""
        }
    ]

def add_ontology_api(api_id, api_url, api_name, ontologies):
    collection_title = 'OntologyAPI'
    ontology_api_ref = db.collection(collection_title)

    document_id = api_id

    data = {
        'api_id': api_id,
        'api_url': api_url,
        'api_name': api_name,
        'ontologies': ontologies
    }

    ontology_api_ref.document(document_id).set(data)
    print(f"Created {document_id} document in the {collection_title} collection")

def ontology_api_etl():
    # Collect OLS data
    ols_data = collect_ols_data()
    
    # Add manual ontologies
    manual_ontologies = add_manual_ontologies()

    # Combine OLS and manual data
    combined_data = ols_data + manual_ontologies

    # Reformat. Group ontologies by api.
    api_data = {}
    for entry in combined_data:
        api_id = entry['api_id']
        if api_id not in api_data:
            api_data[api_id] = {
                'api_url': entry['api_url'],
                'api_name': entry['api_name'],
                'ontologies': {}
            }
        
        ontology_id = entry['ontology_code']
        api_data[api_id]['ontologies'][ontology_id] = {
            'ontology_title': entry['ontology_title'],
            'ontology_code': entry['ontology_code'],
            'curie': entry['curie'],
            'system': entry['system'],
            'version': entry['version'],
        }

    # Insert data into Firestore
    for api_id, data in api_data.items():
        add_ontology_api(api_id, data['api_url'], data['api_name'], data['ontologies'])

if __name__ == "__main__":
    main()
