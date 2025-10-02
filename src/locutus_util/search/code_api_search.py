"""
Get metadata for a code using the search_dragon.

python src/dbt_pipeline_utils/scripts/code_api_search.py -ak 'HP:0000828|HP:0000828' -o "HPO, HP" -f 'annotations3.csv'
"""

import argparse
import csv
import pandas as pd
from search_dragon.search import run_search
from locutus_util.common import *
from locutus_util.helpers import logger

from pathlib import Path

def get_onto_data():
    ori = pd.read_csv(LOCUTUS_SYSTEM_MAP_PATH)
    # Create a dictionary from the DataFrame
    onto_data = {}
    for _, row in ori.iterrows():
        key = row[0]
        value = row[1]
        onto_data[key] = value

    return onto_data

def main(codes, ontologies, filepath, results_per_page, start_index):
    annotations = {}
    onto_data = get_onto_data()

    codes = [c.strip() for c in codes.split("|")]
    ontology_param = [c.strip() for c in ontologies.split(",")]

    for keyword in codes:
        logger.info(f"Requesting: {keyword}")
        annotations[keyword]={}

        # TODO: Automate conversions.
        # Apply Ontology prefix conversions when necessary.
        ols_keyword = keyword 
        umls_keyword = keyword.replace('HP:', 'HPO:')
        if keyword.startswith('HP:'):
            ols_keyword = keyword
            umls_keyword = keyword.replace('HP:', 'HPO:')
        if keyword.startswith('HPO:'):
            ols_keyword = keyword.replace('HPO:', 'HP:')
            umls_keyword = keyword

        annotations[keyword]['ols'] = run_search(onto_data, ols_keyword, ontology_param, ['ols'], results_per_page, start_index)
        annotations[keyword]['ols2'] = run_search(onto_data, ols_keyword, ontology_param, ['ols2'], results_per_page, start_index)
        annotations[keyword]['umls'] = run_search(onto_data, umls_keyword, ontology_param, ['umls'], results_per_page, start_index)

    # Format result and output to a CSV file
    with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Write header row (optional, depends on your data structure)
        writer.writerow(["api","searched_code","response_code","display","description","system","code_iri","ontology_prefix"])

        for keyword, results in annotations.items():
            for source, result in results.items():
                if result and result.get('results'):
                    for entry in result['results']:
                        source = source
                        code = entry.get('code', "No results")
                        display = entry.get('display', "No results")
                        description = entry.get('description', "No results")
                        system = entry.get('system', "No results")
                        code_iri = entry.get('code_iri', "No results")
                        ontology_prefix = entry.get('ontology_prefix', "No results")
                        writer.writerow([source, keyword, code, display, description, system, code_iri, ontology_prefix])
                else:
                    writer.writerow([source, keyword, "No results", "No results", "No results", "No results", "No results", "No results"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get metadata for a code using the available locutus OntologyAPI connection.")
    
    parser.add_argument("-ak", "--all_keywords", required=True, help="A string value containing words to search with the API. Delimeter |")
    parser.add_argument("-o", "--ontologies", required=False, default='HP,HPO', help="A string value containing the ontology_prefixes to use in the searh")
    parser.add_argument("-f","--filepath",required=False, default = 'annotations.csv', help="The output filename. Path from root.",)
    parser.add_argument("-r", "--results_per_page", required=False, default = 1, help="How many pages should the API return per request")
    parser.add_argument("-s", "--start_index", required=False, default = 1, help="Which page should be returned")
    parser.add_argument("-i", "--input_type", required=False, default = 1, help="Which page should be returned")

    args = parser.parse_args()

    main(codes=args.all_keywords,
         ontologies=args.ontologies,
         filepath=args.filepath,
         results_per_page=args.results_per_page,
         start_index=args.start_index
         )
