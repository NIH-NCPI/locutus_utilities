#!/usr/bin/env python
'''
1. Cleans a datafile column that contains codes. 
Expects a column with data similar to: '|HP:0004323|HP:0000234|''|HP:0004323||HP:0000234|'

2. Get metadata for a code using the available locutus OntologyAPI class.

./scripts/get_code_metadata.py -df 'data/{study}/{filename}.csv' -c '{col_to_clean}' -o 'HP,HPO,{Other prefixes}' -f 'data/{study}/cleaned_annotations.csv'
'''

import argparse
from locutus_util.helpers import logger
from locutus_util.search.clean_code_col import *
from locutus_util.search.code_api_search import main as search

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get metadata for a code using the available locutus OntologyAPI connection.")

    parser.add_argument("-df", "--data_file", required=True, help="File containing the codes requiring metadata. Format: 'path/to/datafile.csv'")
    parser.add_argument("-c", "--column", required=True, help="Column name containing the codes requiring metadata. The utils can do some amount of cleaning. # Format: 'ExactFieldName'")
    parser.add_argument("-o", "--ontologies", required=False, default='HP,HPO', help="A string value containing the ontology_prefixes to use in the searh")
    parser.add_argument("-f","--filepath",required=False, default = 'annotations.csv', help="The output filename. Path from root.",)
    parser.add_argument("-r", "--results_per_page", required=False, default = 1, help="How many pages should the API return per request. Both APIs give a response for each code.")
    parser.add_argument("-s", "--start_index", required=False, default = 1, help="hich page should be returned. Note: most likely you don't want to use this.")

    args = parser.parse_args()

    # Cleans code columns.
    clean_code_df = clean_codes(
        df=args.data_file, column=args.column, curies=args.ontologies
    )

    # Join all unique, clean codes, into a single string to use as the api search input.
    unique_codes=set()
    for row in clean_code_df['cleaned_col']:
        unique_codes.update(row.split('|'))
    all_keywords = '|'.join(unique_codes) 
    logger.debug(all_keywords)

    search(codes=all_keywords, # Format: 'word1|word2|word3'
         ontologies=args.ontologies,
         filepath=args.filepath,
         results_per_page=args.results_per_page,
         start_index=args.start_index
         )
