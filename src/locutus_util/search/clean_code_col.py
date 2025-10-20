'''
Cleans a datafile column that contains codes. 
Expects a column with data similar to: '|HP:0004323|HP:0000234|''|HP:0004323||HP:0000234|'
'''

import argparse
import re
import pandas as pd
from locutus_util.helpers import logger



def clean_codes(codes, curies):
    # TODO: Split and strip whitespace on each code, before joining back

    for c in curies:  # Ensure codes are separated by the |
        codes = codes.replace(c, f"|{c}").replace(c, f"{c}:").replace(f"{c}::", f"{c}:")
    codes = codes.replace(" ", "")  # Whitespace
    codes = codes.replace("''", "").replace('"', "")  # Quotations
    codes = codes.replace("Ê", "")  # Sp characters
    codes = codes.replace("|||", "|").replace("||", "|")  # Multiple bars
    codes = codes.strip("|")  # Leading and trailing bars
    return codes

def is_valid_format(code):
    # Check format STRING:12345 (uppercase string, colon, string)
    return bool(re.fullmatch(r'[A-Z]+:.*?', code))

def create_flag_column(codes):
    # Check if each code matches the valid format
    return [is_valid_format(code) for code in codes.split('|') if code.strip()]

def main(df,column,curies):
    df = pd.read_csv(df)
    curies = curies.split(",")

    df['cleaned_col'] = df[column].apply(lambda x: clean_codes(x, curies))
    df['correct_format'] = df['cleaned_col'].apply(create_flag_column)

    t=df[['cleaned_col','correct_format']]
    t.to_csv('col_clean.csv', index=False)

    # Catch all codes that might not be cleaned properly
    questionable = df[df['correct_format'].apply(lambda x: not all(x))]
    if len(questionable)>=1:
        logger.warning(f': {questionable[['cleaned_col','correct_format']]}')

    logger.info('Clean codes are returned')
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get metadata for a code using the available locutus OntologyAPI connection.")
    
    parser.add_argument("-df", "--data_file", required=True, help="File containing the codes requiring metadata. Format: 'path/to/datafile.csv'")
    parser.add_argument("-c", "--column", required=True, help="Column name containing the codes requiring metadata. The utils can do some amount of cleaning. # Format: 'ExactFieldName'")
    parser.add_argument("-o", "--ontologies", required=True, help="List of ontology prefixes")

    args = parser.parse_args()

    main(df=args.data_file, column=args.column, curies=args.ontologies)
