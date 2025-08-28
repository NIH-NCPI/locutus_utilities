import argparse
import csv
from locutus_util import init_database
from locutus_util.helpers import update_gcloud_project
from locutus_util.common import SEED_DATA_PATH



def read_csv_and_organize(file_path):
    """
    Reads a CSV file and organizes the data by terminology_id.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary of terminology data grouped by terminology_id.
    """
    terminology_data = {}
    with open(file_path, mode="r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            terminology_id = row["terminology_id"]
            # Create an entry for the terminology if it doesn't exist
            if terminology_id not in terminology_data:
                terminology_data[terminology_id] = {
                    "id": row["terminology_id"],
                    "description": row["terminology_description"],
                    "name": row["terminology_name"],
                    "resource_type": row["terminology_resource_type"],
                    "codes": [],
                }
            # Add code details to the terminology
            terminology_data[terminology_id]["codes"].append(
                {
                    "code": row["code"],
                    "system": row["system"],
                    "display": row["display"],
                    "description": row["description"],
                }
            )
    return terminology_data


def insert_into_firestore(db, data):
    for terminology_id, document_data in data.items():
        # Define the document reference with terminology_id
        terminology_ref = db.collection("Terminology").document(terminology_id)
        # Set the document data
        terminology_ref.set(document_data)
        print(f"Inserted document for terminology_id: {terminology_id}")


def seed_data_etl(db_client):
    try:
        # Read and organize the CSV data
        terminology_data = read_csv_and_organize(SEED_DATA_PATH)

        # Insert the organized data into Firestore
        insert_into_firestore(db_client, terminology_data)

        print("CSV data has been successfully inserted into Firestore.")
    except Exception as e:
        print(f"Error: {e}")


def exec(args=None):
    locutus_project = {
        "DEV": "locutus-dev",
        "UAT": "locutus-uat",
        "PROD": "locutus-407820",
        "ALPHA": "locutus-alpha",
    }

    parser = argparse.ArgumentParser(
        description="Seed terminology data into Firestore."
    )
    parser.add_argument(
        "-e", "--env", choices=locutus_project.keys(), help="Locutus environment to use"
    )
    parser.add_argument("-p", "--project", type=str, help="GCP Project to edit")
    parser.add_argument("--mongo-uri", type=str, help="Mongo DB URI with db included")

    args = parser.parse_args(args)

    client = None
    if args.mongo_uri:
        client = init_database(mongo_uri=args.mongo_uri, missing_db_ok=True)

    else:
        if args.env is not None:
            project_id = locutus_project[args.env]
        else:
            project_id = args.project

        if project_id is not None:
            client = init_database(project_id=project_id)

    seed_data_etl(client)

if __name__ == "__main__":
    exec()