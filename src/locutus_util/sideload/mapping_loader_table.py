#!/usr/bin/env python
'''
Map existing `Table.variables` to the `mappings` specified in a csv. 
See more in the README.md
'''

import argparse
import csv
import logging
from datetime import date
from locutus.model.table import Table
from locutus.model.user_input import MappingConversations
from locutus.model.terminology import Terminology as Term, CodingMapping
from locutus_util.helpers import update_gcloud_project, set_logging_config, load_ontology_lookup

from locutus_util.common import LOGS_PATH, LOCUTUS_SYSTEM_MAP_PATH

locutus_project = {
    "DEV": "locutus-dev",
    "UAT": "locutus-uat",
    "PROD": "locutus-407820",
    "ALPHA": "locutus-alpha",
    "UNI": "mapdragon-unified",
}

def process_csv(file, table):

    system_lookup = load_ontology_lookup()
    # Build a lookup that we can use to map the variable names to
    # their respective terminologies
    enumerations = {}
    # varname => reference to terminology
    for variable in table.variables:
        # Map to the Enumerations if available
        if hasattr(variable, "enumerations"):
            enumerations[variable.code] = variable.enumerations
            logging.info(f"Setting enumerations for {variable.enumerations}")
        elif not hasattr(variable, "enumerations"):
            enumerations[variable.code] = variable.code
            logging.info(f"Setting enumerations for {variable.code}")
        else:
            logging.info(
                f"SKIPPING:{variable.code}, DTYPE:{variable.data_type}, No enumerations to set. ")
    logging.info(enumerations)

    illegal_enums = ['NA',""]

    csv_reader = csv.DictReader(file)
    user_input = MappingConversations()
    for row in csv_reader:
        source_variable = row["source_variable"]  # Terminology

        # The code being mapped. A Variable, or a Variable's Enumeration.
        source_enumeration = row.get("source_enumeration")
        if source_enumeration is None or source_enumeration.strip() in illegal_enums:
            source_enumeration = source_variable
            logging.info(f"MAPPING {source_variable} to 'source_variable' because no source_enumeration is supplied.")
        else:
            source_enumeration = source_enumeration.strip()  

        system = row.get("system")
        # Get and clean system
        if system in system_lookup:
            original_system = system
            system = system_lookup[system]
            logging.info(f"Enum {source_enumeration}. Remapped system {original_system} to: {system}")
        if system not in system_lookup.values():
            logging.warning(f'Invalid system for enum {source_enumeration}. "{system}" not found in the lookup file {LOCUTUS_SYSTEM_MAP_PATH}')

        codes = [x.strip() for x in row["code"].split(",")]
        displays = row.get("display").split(",")
        editor = row["provenance"]
        comment = row["comment"]

        if (
            row["display"]
            == "dyskinesia with orofacial involvement, dyskinesia with orofacial involvement, autosomal dominant"
        ):
            displays = (
                "dyskinesia with orofacial involvement, autosomal dominant".split(",")
            )

        index = 0
        if len(codes) == 1:
            displays = [row.get("display")]
        assert len(codes) == len(
            displays
        ), f"Error! Does not compute! \n{row}\n\t{len(codes)} != {len(displays)}"
        for code in codes:
            display = displays[index]

            index += 1
            if source_variable in enumerations:
                if code != "NA":
                    logging.info(
                        f"{source_variable}.{source_enumeration} + {code}({display})"
                    )

                    # Use the Table's shadow Terminology to map Variables
                    if source_variable == source_enumeration:
                        t = table.terminology.dereference()
                    # Use the Enumeration's Terminology to map Enumerations
                    else:
                        t = enumerations[source_variable].dereference()

                    codings = [
                        x
                        for x in t.mappings(source_enumeration)[source_enumeration]
                        if x.code != code
                    ]
                    codings.append(
                        CodingMapping(code=code, display=display, system=system)
                    )
                    t.set_mapping(
                        source_enumeration, codings=codings, editor=editor
                    )
                    if comment is not None and comment != "NA":
                        user_input.create_or_replace_user_input(
                            resource_type="Terminology",
                            collection_type="user_input",
                            id=t.id,
                            code=code,
                            mapped_code=code,
                            type="mapping_conversations",
                            body=comment,
                        )
                    else:
                        logging.info(f"skipping {source_variable}")


def load_data(project_id, table_id, file):
    _log_file = f"{LOGS_PATH}/{date.today()}_{project_id}_data_load.log"

    # Set logging configs
    set_logging_config(log_file=_log_file)
    logging.info(f"Log file created: {_log_file}")

    # Set the correct project
    logging.info(f"Setting GCP project: {project_id}")
    update_gcloud_project(project_id)

    # Grab the Table from the database via the usual model backend stuff
    logging.info(f"Starting CSV processing for file: {file.name}")
    table = Table.get(table_id)
    process_csv(file, table)
    logging.info("CSV processing completed.")


def main():
    parser = argparse.ArgumentParser(description="Load CSV data into Firestore.")
    parser.add_argument(
        "-e",
        "--env",
        choices=["DEV", "UAT", "ALPHA", "PROD", "UNI"],
        help="Locutus environment to use",
    )
    parser.add_argument(
        "-p",
        "--project-id",
        help="GCP Project to edit (if not part of a standard environment)",
    )
    parser.add_argument("-f", "--file", type=argparse.FileType("rt"))

    parser.add_argument(
        "-t", "--table-id", help="Which table the data can be found in."
    )

    args = parser.parse_args()

    if args.env is not None:
        project_id = locutus_project[args.env]
    else:
        project_id = args.project_id

    load_data(project_id=project_id, table_id=args.table_id, file=args.file)

if __name__ == "__main__":
    main()
