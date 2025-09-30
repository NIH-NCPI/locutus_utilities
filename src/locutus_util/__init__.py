
_db_client = None 
import subprocess
import logging


def update_gcloud_project(project_id):
    """Update the active Google Cloud project."""
    command = ["gcloud", "config", "set", "project", project_id]
    
    try:
        logging.info(f"Updating Google Cloud project to: {project_id}")
        subprocess.run(command, check=True)
        logging.info(f"Project updated successfully: {project_id}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error updating project: {e}")

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
