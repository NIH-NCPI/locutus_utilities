#!/usr/bin/env python3
'''
Scans through all of the mappings in a db and returns distinct systems.
'''

import argparse
from google.cloud import firestore
import logging
from datetime import datetime
from locutus_util.common import LOGS_PATH
from locutus_util.helpers import (set_logging_config, write_file)
from locutus.model.ontologies_search import OntologyAPISearchModel


def get_all_systems(db, all_sys_path):
    """
    Scans the 'mappings' subcollection of all documents in 'Terminology',
    and returns a list of codes that are missing the 'system' field or have it null/empty.
    """
    existing_systems = set()

    term_docs = db.collection("Terminology").list_documents()
    total_missing = 0

    for term_doc in term_docs:
        term_id = term_doc.id
        mappings_ref = term_doc.collection("mappings")
        # if total_missing >= 10:
        #     continue
        for mapping_doc in mappings_ref.stream():
            data = mapping_doc.to_dict()
            codes = data.get("codes", [])
            for code_entry in codes:
                system = code_entry.get("system")
                existing_systems.add(system)

    # Convert the set to a list of dicts
    system_data = [{"system": value if value is not None else "UNKNOWN"} for value in sorted(s for s in existing_systems if s is not None)]

    # Then call your write_file function
    write_file(all_sys_path, system_data, sort_by_list=["system"])


def main(project_id,database):

    _log_file = f"{LOGS_PATH}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}_{database}_system_remediation.log"
    all_sys_path = f"{LOGS_PATH}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}_{database}_existing_systems.csv"


    # Set logging configs -log file created in data/logs
    set_logging_config(log_file = _log_file)

    # Initiate Firestore client and setting the project_id
    db = firestore.Client(project=project_id, database=database)
    
    empty_systems = get_all_systems(db, all_sys_path)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Delete Terminology documents with slashes in their index.")
    parser.add_argument('-p', '--project_id', required=True, help="GCP Project to edit")
    parser.add_argument('-db', '--database', required=False, help="Database to edit. Will edit the projects default db if not set here.")


    args = parser.parse_args()
    

    main(project_id=args.project_id,database=args.database)
