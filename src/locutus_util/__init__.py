_db_client = None
import os
import json
from pathlib import Path
import subprocess
import logging
from datetime import date

# URLs
OLS_API_BASE_URL = "https://www.ebi.ac.uk/ols4/api/"
MONARCH_API_BASE_URL = "https://api-v3.monarchinitiative.org/v3/api/search?q="
LOINC_API_BASE_URL = "https://loinc.regenstrief.org/searchapi/"
UMLS_API_BASE_URL = "https://uts-ws.nlm.nih.gov/rest/"


# Dirs and file paths
HOME_DIR = Path.home()
CONFIG_FILE_PATH = HOME_DIR / ".mapdragon/config.json"

ROOT_DIR = Path(__file__).parent.parent.parent.resolve()
DATA_DIR = Path(f"{ROOT_DIR}/data")
LOGS_PATH = Path(f"{DATA_DIR}/logs")
SEED_ETL_DIR = Path(f"{DATA_DIR}/seed_etl")
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

# Setup Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_file = LOGS_PATH / f"{date.today()}"

# Prevent duplicate handlers
if logger.hasHandlers():
    logger.handlers.clear()

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)


def update_gcloud_project(project_id):
    """Update the active Google Cloud project."""
    command = ["gcloud", "config", "set", "project", project_id]

    try:
        logging.info(f"Updating Google Cloud project to: {project_id}")
        subprocess.run(command, check=True)
        logging.info(f"Project updated successfully: {project_id}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error updating project: {e}")


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


CONFIGS = {}


def load_configurations():
    """Load configurations from the config file if it exists."""
    global CONFIGS

    try:
        # Ensure the parent directory exists
        if not os.path.exists(os.path.dirname(CONFIG_FILE_PATH)):
            os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
            logger.debug(
                f"Created configuration directory: {os.path.dirname(CONFIG_FILE_PATH)}"
            )

        # Check if the configuration file exists
        if os.path.exists(CONFIG_FILE_PATH):
            logger.info(f"Configuration file found: '{CONFIG_FILE_PATH}'")
            with open(CONFIG_FILE_PATH, "r") as config_file:
                try:
                    CONFIGS = json.load(config_file)

                    # Resolve environment variables if any value starts with "$"
                    for key, value in CONFIGS.items():
                        if isinstance(value, str) and value.startswith("$"):
                            env_var = value[1:]
                            CONFIGS[key] = os.getenv(env_var, value)

                except json.JSONDecodeError as e:
                    logger.error(
                        f"Error: Configuration file {CONFIG_FILE_PATH} is not in valid JSON format. Error: {str(e)}"
                    )
                    CONFIGS = {}
        else:
            logger.debug(f"No configuration file found at {CONFIG_FILE_PATH}.")

    except Exception as e:
        logger.error(f"Unexpected error while loading configurations: {str(e)}")
        CONFIGS = {}


load_configurations()


def resolve_environment(env_or_uri):
    """
    Resolve the environment URI from the global configurations or use the provided value.
    """
    envs = CONFIGS.get("envs", {})

    if env_or_uri is None:
        return "http://localhost:8080"

    if env_or_uri in envs:
        value = CONFIGS["envs"][env_or_uri]

        if value.startswith("$"):
            env_var = value[1:]  # Remove the "$" prefix
            value = os.getenv(env_var, value)  # Resolve environment variable
            
        logger.info(
            f"Environment '{env_or_uri}' found in configuration file. Using value: {CONFIGS["envs"][env_or_uri]}"
        )
        return value
        
    logger.info(
        f"Environment '{env_or_uri}' not found in configuration file. Using provided URI: {env_or_uri}"
    )
    return env_or_uri


def init_database(mongo_uri=None, project_id=None, missing_db_ok=False):
    """Initialize the database, leave mongo_uri as None to use a traditional firestore connection"""

    global _db_client
    if _db_client is None:
        if mongo_uri:
            from locutus.storage.mongo import persistence

        else:
            from locutus.storage.firestore import persistence

            if project_id:
                update_gcloud_project(project_id)

        _db_client = persistence(mongo_uri, missing_db_ok)

    return _db_client 
