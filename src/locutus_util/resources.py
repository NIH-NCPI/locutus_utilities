import os
import inspect

# Determine the root directory
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Directory paths
SRC_PATH = os.path.join(base_path, 'src')
TOOLS_PATH = os.path.join(SRC_PATH, 'tools')
LOCUTUS_UTIL_PATH = os.path.join(SRC_PATH, 'locutus_util')
STORAGE_PATH = os.path.join(LOCUTUS_UTIL_PATH, 'storage')
STORAGE_LOOKUP_PATH = os.path.join(STORAGE_PATH, 'lookup_tables')

# File paths
ONTOLOGY_API_LOOKUP_TABLE_PATH = os.path.join(STORAGE_LOOKUP_PATH, 'ontology_definition.csv')

# API URLs
OLS_API_BASE_URL = "https://www.ebi.ac.uk/ols4/api/"
MONARCH_API_BASE_URL = "https://api-v3.monarchinitiative.org/v3/api/search?q="
LOINC_API_BASE_URL = "https://loinc.regenstrief.org/searchapi/"