import os
import inspect

base_path = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))


# Directory paths
TOOLS_PATH = os.path.join(base_path, 'utils')
STORAGE_PATH = os.path.join(base_path, 'storage')
STORAGE_LOOKUP_PATH = os.path.join(STORAGE_PATH, 'lookup_tables')

# File paths
ONTOLOGY_API_LOOKUP_TABLE_PATH = os.path.join(STORAGE_LOOKUP_PATH, 'ontology_definition.csv')

# API URLs
OLS_ONTOLOGIES_URL = "https://www.ebi.ac.uk/ols4/api/ontologies"