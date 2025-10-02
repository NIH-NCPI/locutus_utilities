import os
from pathlib import Path

# URLs
OLS_API_BASE_URL = "https://www.ebi.ac.uk/ols4/api/"
MONARCH_API_BASE_URL = "https://api-v3.monarchinitiative.org/v3/api/search?q="
LOINC_API_BASE_URL = "https://loinc.regenstrief.org/searchapi/"
UMLS_API_BASE_URL = "https://uts-ws.nlm.nih.gov/rest/"


# Environment variables
def get_api_key(api_id):
    if api_id == "umls":
        API_KEY = os.getenv("UMLS_API_KEY")
    if not API_KEY:
        raise ValueError(
            "API_KEY for {api_id} is not set in the environment variables."
        )
    else:
        return API_KEY


# Dir file paths
HOME_DIR = Path.cwd().resolve()
DATA_DIR = Path(f"{HOME_DIR}/data")
LOGS_PATH = Path(f"{DATA_DIR}/logs")
INPUT_PATH = Path(f"{DATA_DIR}/input")
OUTPUT_PATH = Path(f"{DATA_DIR}/output")
ONTOLOGY_DATA_PATH = Path(f"{INPUT_PATH}/ontology_data")
SIDELOAD_PATH = Path(f"{INPUT_PATH}/sideload_data")

# Data file paths
ONTOLOGY_API_PATH = Path(f"{ONTOLOGY_DATA_PATH}/ontology_api.csv")
SEED_DATA_PATH = Path(f"{ONTOLOGY_DATA_PATH}/seed_data.csv")
INCLUDED_ONTOLOGIES_PATH = Path(f"{ONTOLOGY_DATA_PATH}/included_ontologies.csv")
MANUAL_ONTOLOGY_TRANSFORMS_PATH = Path(
    f"{ONTOLOGY_DATA_PATH}/manual_ontology_transformations.csv"
)
LOCUTUS_SYSTEM_MAP_PATH = Path(f"{ONTOLOGY_DATA_PATH}/locutus_system_map.csv")

# Values
BATCH_SIZE = 10
COL_TIME_LIMIT = 300
SUB_TIME_LIMIT = 60

# Options
# Script options
UPDATE_ONTOLOGY_API = 'update_ontology_api'
UPDATE_SEED_DATA = 'update_seed_data'
DELETE_PROJECT_DATA = 'delete_project_data'
RESET_DATABASE = 'reset_database'
# Ontology_api_etl options
FETCH_AND_UPLOAD = 'fetch_and_upload'
UPLOAD_FROM_CSV = 'upload_from_csv'
UPDATE_CSV = 'update_csv'
