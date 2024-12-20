
# URLs
OLS_API_BASE_URL = "https://www.ebi.ac.uk/ols4/api/"
MONARCH_API_BASE_URL = "https://api-v3.monarchinitiative.org/v3/api/search?q="
LOINC_API_BASE_URL = "https://loinc.regenstrief.org/searchapi/"

# Filepaths 
LOGS_PATH = 'data/logs/'
ONTOLOGY_API_PATH = 'data/ontology_api.csv'
SEED_DATA_PATH = 'data/seed_data.csv'
INCLUDED_ONTOLOGIES_PATH = 'data/included_ontologies.csv'

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
