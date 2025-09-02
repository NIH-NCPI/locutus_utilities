#!/usr/bin/env python

from locutus.model.study import Study 
from locutus.model.datadictionary import DataDictionary 
from locutus.model.table import Table
from locutus.model.terminology import Terminology
from locutus.model.coding import Coding, CodingMapping 
from locutus.model.provenance import Provenance
from locutus.model.onto_api_preference import OntoApiPreference 
from locutus.model.user_input import MappingConversation, MappingVote, UserInput 
from locutus import persistence

from locutus.model.exceptions import CodeNotPresent

from argparse import ArgumentParser, FileType
import json
import sys

from rich import print

import pdb

def LoadOntologyAPI(api_content):
    for onto in api_content:
        persistence().db["OntologyAPI"].insert_one(api_content[onto])
        print(f"{onto}\t{len(api_content[onto]['ontologies'])}")

def LoadTerminologies(terms):
    for id, term in terms.items():

        """api_prefs = {}
        if "subcollections" in term:
            if "onto_api_preference" in term['subcollections']:
                if "self" in term['subcollections']['onto_api_preference']:
                    api_prefs = term['subcollections']['onto_api_preference']['self']
        """

        preferred_terminologies = []
        if "subcollections" in term:
            if "preferred_terminology" in term['subcollections']:
                preferred_terminologies = term['subcollections']['preferred_terminology']['self']['references']
        url = term.get('url')
        if url is None:
            url=term['codes'][0]['system']

        if "codes" not in term:
            print(term)
            print("Unable to find a code array")
            pdb.set_trace()

        codes = []
        for coding in term['codes']:
            if coding['code'] != "":
                codes.append(coding)

        try:
            t = Terminology(
                id=term['id'],
                name=term.get('name'),
                description=term['description'],
                url=url,
                codes = codes,
                preferred_terminologies=preferred_terminologies
            )
        except ValueError as e:
            print(term)
            pdb.set_trace()

        if "subcollections" in term:
            if 'mappings' in term['subcollections']:
                for code, item in term['subcollections']['mappings'].items():
                    if len(item['codes']) > 0:
                        try:
                            t.set_mapping(item['code'], item['codes'], editor="db-copy")
                        except CodeNotPresent as e:
                            print(f"No code, {code}, found to map codes to.")

            if 'onto_api_preference' in term['subcollections']:
                for code, item in term['subcollections']['onto_api_preference'].items():
                    prefs = item['api_preference']
                    for api, ontos in prefs.items():
                        t.add_api_preferences(api, ontos)
            if 'user_input' in term['subcollections']:
                for key, uinput in term['subcollections']['user_input'].items():
                    if "mapping_votes" in uinput:
                        for user, vote in uinput['mapping_votes'].items():
                            UserInput.create_or_replace_user_input(
                                resource_type="",
                                collection_type="",
                                id=t.id,
                                code=uinput['code'],
                                mapped_code=uinput['mapped_code'],
                                type='mapping_votes',
                                input_value=vote['vote'],
                                editor=user,
                                timestamp=vote['date']
                            )
                    if "mapping_conversations" in uinput:
                        for cnv in uinput['mapping_conversations']:
                            UserInput.create_or_replace_user_input(
                                resource_type="",
                                collection_type="",
                                id=t.id,
                                code=uinput['code'],
                                mapped_code=uinput['mapped_code'],
                                type='mapping_conversations',
                                input_value=cnv['note'],
                                editor=cnv['user_id'],
                                timestamp=cnv['date']
                            )
            if "provenance" in term['subcollections']:
                # Clear out any provenance that we might have created just now 
                # and replace it with what was found in the original data
                for prov in Provenance.find({
                    "terminology_id": t.id
                }, return_instance=True):
                    if prov.target not in [None, "", "self"]:
                        prov.delete(hard_delete=True)
                
                for target, provenance in term['subcollections']['provenance'].items():
                    for prov in provenance['changes']:
                        t.add_provenance(
                            change_type=prov['action'],
                            editor=prov.get("editor"),
                            timestamp=prov.get("timestamp"),
                            target=prov.get("target"),
                            new_value=prov.get("new_value"),
                            old_value=prov.get("old_value")
                        )

        t.save()

def LoadTable(tables):
    for id, table_content in tables.items():
        if table_content.get('code') is None:
            print(table_content)
            pdb.set_trace()
        t = Table(
            id=table_content.get('id'),
            name=table_content.get('name'),
            code=table_content.get('code'),
            url=table_content.get('url'),
            description=table_content.get('description'),
            filename=table_content.get('filename'),
            terminology=table_content.get('terminology')
        )       
        t.save()

def LoadDataDictionaries(dds):
    for id, dd_content in dds.items():
        d = DataDictionary(
            id=dd_content.get('id'),
            name=dd_content.get('name'),
            description=dd_content.get('description'),
            tables=dd_content.get('tables')
        )
        d.save()

def LoadStudy(studies):
    for id, study in studies.items():
        s = Study(
            id=study.get('id'),
            name=study.get('name'),
            description=study.get('description'),
            identifier_prefix=study.get('identifier_prefix'),
            title=study.get('title'),
            url=study.get('url'),
            datadictionary=study.get('datadictionary')
        )
        s.save()

def LoadData(db_contents):
    LoadOntologyAPI(db_contents['collections']['OntologyAPI'])
    LoadTerminologies(db_contents['collections']['Terminology'])
    LoadTable(db_contents['collections']['Table'])
    LoadDataDictionaries(db_contents['collections']['DataDictionary'])
    LoadStudy(db_contents['collections']['Study'])

def main(args=None):

    parser = ArgumentParser(
        description="Load db data from JSON file into locutus"
    )
    parser.add_argument(
        "-f", "--json-file", 
        type=FileType('rt'), 
        help="JSON file containing DB contents"
    )
    parser.add_argument(
        "-db", "--database-uri", 
        default="mongodb://localhost:27017/experiment",
        # default="mongodb://localhost:27017/locutus",
        help="Specify DB URI (default: mongodb://localhost:27017/locutus)"
    )
    parser.add_argument(
        "--reset",
        action='store_true',
        help="Clear contents" 
    )
    args = parser.parse_args(args)

    client = persistence(mongo_uri=args.database_uri, missing_ok=True)
    print(f"[green]Database Server:[/green] [yellow]{args.database_uri}[/yellow]")

    if args.reset:
        print(f"[red]Warning:[/red] You are about to drop the entire database, {client.db_name}.")
        print(f"[red][bold]This can not be undone![/bold][/red]")
        if input(f"To proceed, type {client.db_name}: ").lower() == client.db_name:
            client.client.drop_database(client.db_name)
        else:
            print(f"[red]Unable to continue due to incorrect input[/red]")
            sys.exit(1)

    # pdb.set_trace()
    dbcontent = json.load(args.json_file)
    LoadData(dbcontent)

if __name__=="__main__":
    main()
        
    
