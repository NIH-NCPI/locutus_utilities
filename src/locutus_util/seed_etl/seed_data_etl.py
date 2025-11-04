"""
Runs off of the data/seed_etl/seed_config.yml
For more information, see /locutus_util/seed_etl/README

Run examples
`python seed_etl/seed_database.py`
Options: 
-e change the baseurl from localhost to another url
-a change the default action from seeding the db to deleting from the db.

"""

import argparse
import csv
import requests
from locutus_util.helpers import read_file, delete_codes
from locutus_util.common import SEED_ETL_DIR
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_for_loc(file_path):
    terminology_data = {}

    with open(file_path, mode="r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            terminology_id = row["terminology_id"]
            if terminology_id not in terminology_data:
                terminology_data[terminology_id] = {
                    "id": row["terminology_id"],
                    "description": row["terminology_description"],
                    "name": row["terminology_name"],
                    "url": row["system"],
                    "resource_type": row["terminology_resource_type"],
                    "codes": [],
                }
            terminology_data[terminology_id]["codes"].append(
                {
                    "code": row["code"],
                    "display": row["display"],
                    "description": row["description"],
                    "system": row['system']
                }
            )
    return terminology_data

def save_terminology(base_url, terminology):
    response = {}
    for keys, values in terminology.items():
        t_id = values.get('id')
        endpoint = f"{base_url}/api/Terminology/{t_id}"
        headers = {"Content-Type": "application/json"}
        try:
            logger.info(endpoint)
            res = requests.put(endpoint, json=values, headers=headers)
            response[keys] = {"status_code": res.status_code, "response": res.text}
            if res.status_code != 200:
                logger.error(f"Failed to save terminology {keys}: {res.status_code} - {res.text}")
            else:
                logger.info(f"Successfully saved terminology {keys}")
        except Exception as e:
            logger.error(f"Error while saving terminology {keys}: {e}")
    return response


def main():
    parser = argparse.ArgumentParser(description="Load CSV data into Firestore.")
    parser.add_argument(
        '-e',
        '--env',
        default="http://localhost:8080",
        help="Will be used as the base url in an api request to locutus."
    )
    parser.add_argument(
        '-a',
        '--action',
        default="seed",
        help="Choose whether to seed the db with a Terminology, or delete codes from a db Terminology",
        choices=['seed','delete']
    )
    args = parser.parse_args()

    logger.info('STARTED seeding the database')

    # Path to the YAML configuration file
    config_file = SEED_ETL_DIR / "seed_config.yaml"
    config, file_ext = read_file(config_file)

    for file_name, file_config in config.items():
        if file_config.get('seed_db', False): 
            fnames = file_config.get("normalized_data").get('name')
            for file in fnames:
                logger.info(f"Reading config settings for file: {file_name}")
                filepath = SEED_ETL_DIR / file

                if args.action == 'delete' and file_config.get('remove_codes', False) == True:
                    request_body = format_for_loc(filepath)
                    logger.info(f'Deleting from Terminology {file_name}')
                    response = delete_codes(args.env, request_body)
                    logger.info(f'Deleted from Terminology {file_name}')

                if args.action == 'seed':
                    request_body = format_for_loc(filepath)
                    logger.info(f'Saving Terminology {file_name}')
                    response = save_terminology(args.env, request_body)
                    logger.info(f'Saved Terminology {file_name}')

    logger.info(f'COMPLETED process: {args.action}')
if __name__ == "__main__":
    main()