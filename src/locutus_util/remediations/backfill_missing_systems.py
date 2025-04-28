#!/usr/bin/env python3
'''
Suggestion: Uncomment lines 38-39 while doing initial troubleshooting/setup.

Updates the system of a mapping if the attribute is missing, or an empty string.
Searches the Terminology Collections mappings, collecting doc references to update.
Uses locutus/search-dragon to find the systems by searching the defined api(umls only ATM).
Prints a csv of edits to review before performing the update.
    Search for UNKNOWN in the csv, for any issues
After update confirmation, replaces the systems in the docs referenced.
Log will print for confirmation. 
    Check for error messages, and/or run again to scan.

Suggestion: Place both printouts in the ticket for documentation
'''

import argparse
from google.cloud import firestore
import logging
from datetime import datetime
from locutus_util.common import LOGS_PATH
from locutus_util.helpers import (set_logging_config, write_file)
from locutus.model.ontologies_search import OntologyAPISearchModel

def scan(db, issue_log_path):
    """
    Scans the 'mappings' subcollection of all documents in 'Terminology',
    and returns a list of codes that are missing the 'system' field or have it null/empty.
    """
    missing_system_entries = []

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
                if system is None or system == "":
                    proposed_system = propose_system_for_code(code_entry.get("code"))
                    mapping_dict = {
                        "terminology_id": term_id,
                        "mapping_id": mapping_doc.id,
                        "code": code_entry.get("code"),
                        "display": code_entry.get("display"),
                        "system": system,
                        "proposed_system": proposed_system
                    }
                    missing_system_entries.append(mapping_dict)
                    total_missing += 1
                    logging.info(f"Mapping missing proposed_system: {mapping_dict}")
    logging.info(f"Total missing system entries: {total_missing}")


    return missing_system_entries

def propose_system_for_code(code):
    """
    Proposes a system based on the prefix or pattern of the code.
    """
    if not code:
        return None
    
    prefix_map = {
        "SNOMED": "SNOMED",
        "LA": "LOINC",
        "LP": "LOINC",
        "MTH": "MIM",
        "XAO": "XAO",
        "ZFA": "ZFA",
        "UBERON": "UBERON",
        "SO": "SO",
        "OMIT": "OMIT",
        "OBA": "OBA",
        "NCIT": "NCIT",
        "MA": "MA",
        "HP": "HP",
        "FMA": "FMA",
        "BTO": "BTO",
        "ExO": "ExO",
        "EMAPA": "EMAPA",
        "CL": "CL",
        "LEPAO": "LEPAO",
        "NCRO": "NCRO",
        "OARCS": "OARCS",
    }


    for prefix, system in prefix_map.items():
        if code.startswith(prefix):
            return system

    return "UNKNOWN"

def batch_search_concepts(keywords, ontologies, search_api_list=['umls'], results_per_page=10, start_index=0):
    """
    Runs `run_search` for each unique concept in the list and collects the results.

    Args:
        keywords (List): codes
        ontologies (List): List of ontologies to search in.
        search_api_list (List, optional): APIs to use. HARDCODING UMLS
        results_per_page (int): Number of results to retrieve per page.
        start_index (int): Starting index for pagination.

    Returns:
        dict: Dictionary mapping each concept to its corresponding search results.
    """

    # Ensure keywords are valid strings
    valid_strings = [s for s in keywords if isinstance(s, str) and s.strip()]

    simplified_results = {}

    for concept in valid_strings:
        try:
            logging.info(f"Searching for concept: {concept}")
            result = OntologyAPISearchModel.run_search_dragon(
                concept,
                ontologies,
                search_api_list,
                results_per_page=results_per_page,
                start_index=start_index
            )

            # Extract 'system' from the first result in 'results'
            if isinstance(result, dict) and result.get("results"):
                first_hit = result["results"][0]
                system_url = first_hit.get("system", "UNKNOWN")
                simplified_results[concept] = system_url
            else:
                simplified_results[concept] = "UNKNOWN"

        except Exception as e:
            logging.error(f"Error searching for {concept}: {e}")
            simplified_results[concept] = "ERROR"

    return simplified_results

def update_mapping_systems(db, entries):
    """
    Updates Firestore mapping documents with the proposed system values.
    """
    updated_count = 0
    for entry in entries:
        term_id = entry["terminology_id"]
        mapping_id = entry["mapping_id"]
        code_to_update = entry["code"]
        proposed_system = entry["proposed_system"]

        if not all([term_id, mapping_id, code_to_update, proposed_system]) or proposed_system == "UNKNOWN":
            logging.warning(f"Skipping incomplete entry: {entry}")
            continue

        mapping_ref = db.collection("Terminology").document(term_id).collection("mappings").document(mapping_id)
        mapping_data = mapping_ref.get().to_dict()

        if not mapping_data:
            logging.warning(f"Mapping document not found: {term_id}/{mapping_id}")
            continue

        codes = mapping_data.get("codes", [])
        updated = False
        for code_entry in codes:
            if code_entry.get("code") == code_to_update and not code_entry.get("system"):
                code_entry["system"] = proposed_system
                updated = True

        if updated:
            try:
                mapping_ref.update({"codes": codes})
                updated_count += 1
                logging.info(f"Updated mapping: {term_id}/{mapping_id} with system {proposed_system}")
            except Exception as e:
                logging.error(f"Failed to update mapping {term_id}/{mapping_id}: {e}")

    logging.info(f"Updated {updated_count} mappings with proposed systems.")

def main(project_id,database):

    _log_file = f"{LOGS_PATH}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}_{database}_system_remediation.log"
    issue_log_path = f"{LOGS_PATH}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{project_id}_{database}_missing_sys.csv"

    # Set logging configs -log file created in data/logs
    set_logging_config(log_file = _log_file)

    # Initiate Firestore client and setting the project_id
    db = firestore.Client(project=project_id, database=database)
    
    # Find the mappings without systems, proposes systems where possible via the code prefix
    empty_systems = scan(db, issue_log_path)

    if not empty_systems:
        logging.info("No mappings without systems found.")
        return
    
    # Proposes systems, using the locutus search function on each unique code, then sets the system for every mapping missing a system
    # Hardcoded preferred ontologies, and the api to use in the search(params)
    ontologies = ['SNOMEDCT_US','CDCREC'] # preferred ontologies
    # Unique codes to be matched with a system, ignore the ones with proposals already set.
    unique_codes = list({
        entry["code"]
        for entry in empty_systems
        if entry.get("code") and entry.get("proposed_system") == 'UNKNOWN'
        })
    clean_codes = sorted(set(str(code).strip() for code in unique_codes if code))
    code_map = batch_search_concepts(clean_codes, ontologies)
    logging.info(f'maps: {code_map}')
    # Fill in missing proposed_systems from code_map
    for entry in empty_systems:
        code = entry.get("code")
        if code and (entry.get("proposed_system") == "UNKNOWN"):
            mapped_system = code_map.get(code)
            if mapped_system and mapped_system not in ("UNKNOWN", "ERROR"):
                entry["proposed_system"] = mapped_system


    logging.info(f"\nFound {len(empty_systems)} invalid mappings. See: {LOGS_PATH}")

    # Writes a file to review the proposed mappings before running the update.
    write_file(issue_log_path, empty_systems, ["code","mapping_id"])

    confirm = input("Update these mappings? [y/N]: ").strip().lower()

    if confirm == "y":
        update_mapping_systems(db, empty_systems)
    else:
        logging.info("Update declined.")

if __name__ == "__main__":
    # TODO: Separate the jobs so you don't have to hit the db everytime you troubleshoot. For now, limit the scan to reduce cost.
    
    parser = argparse.ArgumentParser(description="Delete Terminology documents with slashes in their index.")
    parser.add_argument('-p', '--project_id', required=True, help="GCP Project to edit")
    parser.add_argument('-db', '--database', required=False, help="Database to edit. Will edit the projects default db if not set here.")


    args = parser.parse_args()
    

    main(project_id=args.project_id,database=args.database)
