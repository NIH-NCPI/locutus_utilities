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
from locutus_util.helpers import read_file, delete_codes, save_terminology
from locutus_util import SEED_ETL_DIR, logger, CONFIGS, CONFIG_FILE_PATH, resolve_environment

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

def main():    

    parser = argparse.ArgumentParser(description="Load CSV data into Firestore.")
    parser.add_argument(
        "-url",
        "--locutus-url",
        help="Will be used as the base URL in an API request to locutus. Use an API URL or environment name from '{CONFIG_FILE_PATH}'.",
    )
    parser.add_argument(
        '-a',
        '--action',
        default="seed",
        help="Choose whether to seed the db with a Terminology, or delete codes from a db Terminology",
        choices=['seed','delete']
    )
    args = parser.parse_args()

    resolved_uri = resolve_environment(args.database_uri)

    logger.info(f"STARTED {args.action}")

    # Path to the YAML configuration file
    config_file = SEED_ETL_DIR / "seed_config.yaml"
    config, file_ext = read_file(config_file)

    for file_name, file_config in config.items():
        if file_config.get("remove_codes", False) != True and file_config.get("remove_codes", False)  != True:
            logger.info(f"SKIPPING {file_name}. Not configured for action '{args.action}'.")
            continue

        if file_config.get('seed_db', False) == True: 
            fnames = file_config.get("normalized_data").get('name')

            for file in fnames:
                logger.debug(f"Reading config settings for file: {file_name}")
                filepath = SEED_ETL_DIR / file

            if args.action == 'seed':
                request_body = format_for_loc(filepath)
                logger.debug(f'Saving Terminology {file_name}')
                save_terminology(resolved_uri, request_body)

        if file_config.get("remove_codes", False) == True:
            fnames = file_config.get("normalized_data").get('name')

            for file in fnames:
                logger.debug(f"Reading config settings for file: {file_name}")
                filepath = SEED_ETL_DIR / file

            if args.action == 'delete':
                request_body = format_for_loc(filepath)
                logger.debug(f'Deleting from Terminology {file_name}')
                delete_codes(resolved_uri, request_body)



    logger.info(f'COMPLETED {args.action}')
if __name__ == "__main__":
    main()
