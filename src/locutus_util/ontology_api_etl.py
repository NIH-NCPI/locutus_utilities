"""This script fetches data from the APIs, combines it with manually 
added ontologies(required when data is missing), and then uploads the structured
data into Firestore under the `OntologyAPI` collection.

Notes:
Option: Filter using an inclusion list(data/included_ontologies). These ontologies
were flagged specifically for inclusion with the idea that others can be excluded. 
The option can be selected at runtime in the arguments(see README for more). If 
not specified the script will default to add all ontologies. FD-1773

Currently filtering out 'loinc' and 'monarch' API ontologies. FD-1703
"""

import argparse
import requests
import pandas as pd
import logging
from google.cloud import firestore
from locutus_util.helpers import update_gcloud_project, set_logging_config
from locutus_util.common import (
    FETCH_AND_UPLOAD,
    UPLOAD_FROM_CSV,
    UPDATE_CSV,
    LOGS_PATH,
    OLS_API_BASE_URL,
    UMLS_API_BASE_URL,
    MONARCH_API_BASE_URL,
    LOINC_API_BASE_URL,
    ONTOLOGY_API_PATH,
    INCLUDED_ONTOLOGIES_PATH,
    get_api_key,
)

# Define URLS, filepaths and other required resources
csv_path = ONTOLOGY_API_PATH  # Location to store fetched data
included_ontologies = pd.read_csv(
    INCLUDED_ONTOLOGIES_PATH
)  # Read in the curated list of ontologies
ols_ontologies_url = f"{OLS_API_BASE_URL}ontologies"
UMLS_API_KEY = get_api_key("umls")
umls_ontologies_url = (
    f"{UMLS_API_BASE_URL}metadata/current/sources?apiKey={UMLS_API_KEY}"
)
# Initialize logger
logger = logging.getLogger(__name__)
log_file = f"{LOGS_PATH}_ontology_api_etl.log"
set_logging_config(log_file)


extracted_data = []  # Collects the manual ontology data

def fetch_data(url):
    response = requests.get(url)
    logger.info(f'{url}')
    if response.status_code == 200:
        return response.json()
    else:
        return None

def collect_ols_data():
    logger.info("Fetching ols data")
    data = fetch_data(ols_ontologies_url)
    logger.info("Transforming ols data")

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


def collect_umls_data():
    """
    Collects ontology data from the UMLS API.

    Returns:
        list: Transformed data from UMLS API.
    """
    logger.info(f"Fetching umls data")

    data = fetch_data(umls_ontologies_url)
    logger.info("Transforming umls data")

    extracted_data = []  # Initialize a list to store the extracted data

    while data:
        results = data.get("result", [])
        if not isinstance(results, list):
            raise TypeError("Expected 'result' to be a list.")

        for item in results:
            # Transform the data into a consistent structure
            extracted_data.append(
                {
                    "api_url": UMLS_API_BASE_URL,
                    "api_id": "umls",
                    "api_name": "UMLS Terminology Services",
                    "ontology_code": item.get("abbreviation", ""),
                    "curie": item.get("abbreviation", ""),
                    "ontology_title": item.get("expandedForm", ""),
                    "system": None,  # Not available at this time.
                    "version": None,  # Not available at this time.
                    "ontology_family": item.get("family", ""),
                }
            )

        # Fetch the next page if available
        next_url = data.get("_links", {}).get("next", {}).get("href")
        if next_url:
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
            'ontology_title': "Mammalian Phenotype Ontology",
            'ontology_code': "mp",
            'curie': "MP",
            'system': "http://purl.obolibrary.org/obo/mp.owl",
            'version': ""
        },
        {
            'api_url': MONARCH_API_BASE_URL,
            'api_id': "monarch",
            'api_name': "Monarch API",
            'ontology_title': "Neurobehavior Ontology",
            'ontology_code': "nbo",
            'curie': "NBO",
            'system': "http://purl.obolibrary.org/obo/nbo.owl",
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

def add_monarch_ontologies():
    """Monarch API does not keep data on the ontologies themselves. Using a
    list of ontologies found in Monarch, backfill the information using the
    data collected from the OLS API.
    
    If some ontologies are not present in OLS, add those with add_manual_ontologies.
    """
    monarch_ontologies = ['CHEBI', 'ECTO', 'GO', 'HP', 'MAXO', 'MONDO', 'MP', 
                          'NBO', 'PATO', 'RO', 'SNOMED', 'UBERON']

    # Create new entries based on existing OLS data
    monarch_ols = []
    for ontology in extracted_data:
        if ontology['curie'] in monarch_ontologies:
            new_entry = {
                'api_url': MONARCH_API_BASE_URL,
                'api_id': "monarch",
                'api_name': "Monarch API",
                'ontology_title': ontology['ontology_title'],
                'ontology_code': ontology['ontology_code'],
                'curie': ontology['curie'],
                'system': ontology['system'],
                'version': ontology['version'],
            }
            monarch_ols.append(new_entry)
    
    return monarch_ols

def add_ontology_api(db, api_id, api_url, api_name, ontologies):
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
    logger.info(f"Created {document_id} document in the {collection_title} collection")

def reorg_for_firestore(filtered_ontologies):
    """
    Reads a CSV file and organizes the data by terminology_id.
    
    Args:
        file_path (str): The path to the CSV file.
    
    Returns:
        dict: A dictionary of terminology data grouped by terminology_id.
    """
    api_data = {}

    # Easier format
    csv_data = filtered_ontologies.to_dict(orient='records')
    included_ontologies = pd.read_csv(INCLUDED_ONTOLOGIES_PATH)

    # Get a list of the curated ontology curies.
    curated_list = included_ontologies[
        included_ontologies["Default to Include"] == "t"
    ]["Id"].str.upper().tolist()

    for entry in csv_data:
        api_id = entry['api_id']
        ontology_id = entry['ontology_code'].upper()

        # Initialize the API entry if it doesn't exist
        if api_id not in api_data:
            api_data[api_id] = {
                'api_url': entry['api_url'],
                'api_name': entry['api_name'],
                'ontologies': {}
            }

        # Only add the ontology if it doesn't already exist and has a curie
        api_data_ontologies = {key.upper(): value for key, value in api_data[api_id]['ontologies'].items()}
        if ontology_id not in api_data_ontologies and entry['curie']:
            api_data[api_id]["ontologies"][ontology_id] = {
                "ontology_title": entry["ontology_title"],
                "ontology_code": entry["ontology_code"].lower(),
                "curie": entry["curie"].upper(),
                "system": entry["system"],
                "version": entry["version"],
                "short_list": ontology_id in curated_list,
            }
    return api_data

def update_seed_data_csv(data):
    # For data lineage
    data = pd.DataFrame(data)
    combined_df_sorted = data.sort_values(by=['curie', 'api_id'])
    combined_df_sorted.to_csv(csv_path, index=False)
    logger.info(f"The ontology_api csv is updated.")


def filter_firestore_ontologies(data, which_ontologies):
    """
    Filter out 'monarch' and 'loinc'
    Filter for the included ontologies(Optional - which_ontologies)
    """
    # Exclude monarch and loinc
    filtered_data = data[~data['api_id'].str.lower().isin(['monarch','loinc'])]

    if which_ontologies == "curated_ontologies_only":

        keepers = included_ontologies[included_ontologies["Default to Include"] == "t"][
            "Id"
        ].to_list()
        filtered_data = filtered_data[(filtered_data["curie"].isin(keepers))]
        logger.info(
            f"Only the curated list of ontologies will be sent to the firestore. \
              This list only includes the reviewed ols ontologies.\
              Any preferred UMLS ontologies may need to be added."
        )

    filtered_ontologies = filtered_data.copy()

    return filtered_ontologies


def ontology_api_etl(project_id, action, which_ontologies):

    # Collect data from sources
    if action in {FETCH_AND_UPLOAD, UPDATE_CSV}:
        # Collect OLS data
        ols_data = collect_ols_data()

        # Collect UMLS data
        umls_data = collect_umls_data()

        # Generate Monarch data
        monarch_data = add_monarch_ontologies()

        # Add manual ontologies
        manual_ontologies = add_manual_ontologies()

        # Combine OLS and manual data
        combined_data = ols_data + umls_data + monarch_data + manual_ontologies

        logger.info(f'count ols data: {len(ols_data)}')
        logger.info(f'count umls data: {len(umls_data)}')

        update_seed_data_csv(combined_data)

    if action in {FETCH_AND_UPLOAD, UPLOAD_FROM_CSV}:
        # Read in data and handle nulls
        csv_data = pd.read_csv(csv_path, keep_default_na=False, na_values=[''])
        csv_data = csv_data.where(pd.notnull(csv_data), None)

        # Only include the cho-simba ones
        filtered_ontologies = filter_firestore_ontologies(csv_data, which_ontologies)

        # Reformat. Group ontologies by api.
        fs_data = reorg_for_firestore(filtered_ontologies)

        # Update the gcloud project
        update_gcloud_project(project_id)

        # Firestore client after setting the project_id
        db = firestore.Client()

        # Insert data into Firestore
        for api_id, data in fs_data.items():
            add_ontology_api(db, api_id, data['api_url'], data['api_name'], data['ontologies'])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="OntologyAPI data into Firestore.")
    parser.add_argument('-p', '--project', required=True, help="GCP Project to edit")
    parser.add_argument(
        '-a', '--action', 
        choices=[FETCH_AND_UPLOAD, UPLOAD_FROM_CSV, UPDATE_CSV],
        default=UPLOAD_FROM_CSV, 
        help=(
            f"{UPLOAD_FROM_CSV}: (Default option) Upload data from existing CSV to Firestore.\n"
            f"{UPDATE_CSV}: Fetch data from APIs and update the CSV file only.\n"
            f"{FETCH_AND_UPLOAD}: Fetch data from APIs and upload to Firestore.\n"
        )
    )
    parser.add_argument(
        "-w",
        "--which_ontologies",
        choices=["curated_ontologies_only", "all_ontologies"],
        required=False,
        default="all_ontologies",
        help=(
            f"curated_ontologies_only: Use the curated list of ontologies.\n"
            f"all_ontologies: Use all ontologies.\n"
        ),
    )

    args = parser.parse_args()

    ontology_api_etl(
        project_id=args.project_id,
        action=args.action,
        which_ontologies=args.which_ontologies,
    )
