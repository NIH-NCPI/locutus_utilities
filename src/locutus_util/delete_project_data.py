
import argparse
from datetime import datetime
from google.cloud import firestore
from locutus_util.common import LOGS_PATH
from locutus_util.helpers import (update_gcloud_project, drop_collection_data,
                                  set_logging_config)


def delete_project_data(project_id):
    """Delete specified collections and documents(seed data) from the specified
    Firestore project.
    Collections and docuements specified will have all sub-files dropped.
    """
    _log_file = f"{LOGS_PATH}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}_delete_project_data.log"

    # Set logging configs -log file created in data/logs
    set_logging_config(log_file = _log_file)

    # Set the correct project
    update_gcloud_project(project_id)

    # Firestore client after setting the project_id
    db = firestore.Client()

    # Loops through Collections. Deletes Collections/Documents/SubCollections/Documents
    drop_collection_data(db)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Delete Firestore collections and their contents.")
    parser.add_argument('-p', '--project_id', required=True, help="GCP Project to edit")

    args = parser.parse_args()

    delete_project_data(project_id=args.project_id)