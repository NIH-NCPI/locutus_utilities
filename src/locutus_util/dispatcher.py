import argparse
from locutus_util.ontology_api_etl import ontology_api_etl
from locutus_util.seed_data_etl import seed_data_etl
from locutus_util.delete_project_data import delete_project_data
from locutus_util.common import (
    FETCH_AND_UPLOAD, UPLOAD_FROM_CSV, UPDATE_CSV,
    UPDATE_ONTOLOGY_API, UPDATE_SEED_DATA, DELETE_PROJECT_DATA,RESET_DATABASE
)

def main():
    parser = argparse.ArgumentParser(
        description="Manage data ETL of data into Firestore."
    )
    parser.add_argument(
        '-p', '--project_id', 
        required=True, 
        help="GCP Project to edit."
    )
    parser.add_argument(
        '-o', '--option', 
        choices=[UPDATE_ONTOLOGY_API, UPDATE_SEED_DATA, DELETE_PROJECT_DATA, RESET_DATABASE],
        required=True,
        help=(
            f"{UPDATE_ONTOLOGY_API}: Update Ontology API data.\n"
            f"{UPDATE_SEED_DATA}: Update Seed Data."
            f"{DELETE_PROJECT_DATA}: Delete all data from the database."
            f"{RESET_DATABASE}: Delete data from the database, then reseed."
        )
    )
    parser.add_argument(
        '-a', '--action',
        choices=[FETCH_AND_UPLOAD, UPLOAD_FROM_CSV, UPDATE_CSV],
        default=UPLOAD_FROM_CSV,
        help=(
            f"{UPLOAD_FROM_CSV}: Upload data from existing CSV to Firestore.\n"
            f"{UPDATE_CSV}: Fetch data from APIs and update the CSV file only.\n"
            f"{FETCH_AND_UPLOAD}: Fetch data from APIs and upload to Firestore.\n"
        )
    )
    args = parser.parse_args()

    # Call the appropriate function with the provided arguments
    if args.option == UPDATE_ONTOLOGY_API:
        ontology_api_etl(project_id=args.project_id, action=args.action)

    elif args.option == UPDATE_SEED_DATA:
        seed_data_etl(project_id=args.project_id)

    elif args.option == DELETE_PROJECT_DATA:
        delete_project_data(project_id=args.project_id)

    elif args.option == RESET_DATABASE:
        delete_project_data(project_id=args.project_id)
        seed_data_etl(project_id=args.project_id)
        ontology_api_etl(project_id=args.project_id, action=args.action)
        
    else:
        print("No actions were taken.")

if __name__ == "__main__":
    main()
