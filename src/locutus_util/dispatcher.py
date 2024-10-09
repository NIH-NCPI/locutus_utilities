import argparse
from locutus_util.ontology_api_etl import ontology_api_etl
from locutus_util.seed_data_etl import seed_data_etl
from locutus_util.common import (
    FETCH_AND_UPLOAD, UPLOAD_FROM_CSV, UPDATE_CSV,
    UPDATE_ONTOLOGY_API, UPDATE_SEED_DATA
)

def main():
    parser = argparse.ArgumentParser(
        description="Manage data ETL of data into Firestore."
    )
    parser.add_argument(
        '-p', '--project', 
        required=True, 
        help="GCP Project to edit."
    )
    parser.add_argument(
        '-o', '--option', 
        choices=[UPDATE_ONTOLOGY_API, UPDATE_SEED_DATA],
        required=True,
        help=(
            f"{UPDATE_ONTOLOGY_API}: Update Ontology API data.\n"
            f"{UPDATE_SEED_DATA}: Update Seed Data."
        )
    )
    parser.add_argument(
        '-a', '--action',
        choices=[FETCH_AND_UPLOAD, UPLOAD_FROM_CSV, UPDATE_CSV],
        default=UPDATE_CSV,
        help=(
            f"{FETCH_AND_UPLOAD}: Fetch data from APIs and upload to Firestore.\n"
            f"{UPLOAD_FROM_CSV}: Upload data from existing CSV to Firestore.\n"
            f"{UPDATE_CSV}: Fetch data from APIs and update the CSV file only."
        )
    )
    args = parser.parse_args()

    # Call the appropriate function with the provided arguments
    if args.option == UPDATE_ONTOLOGY_API:
        ontology_api_etl(project_id=args.project, action=args.action)

    elif args.option == UPDATE_SEED_DATA:
        seed_data_etl(project_id=args.project)
        
    else:
        print("No actions were taken.")

if __name__ == "__main__":
    main()
