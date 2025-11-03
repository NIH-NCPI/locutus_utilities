"""
Runs off of the data/seed_etl/seed_config.yml
For more information, see /locutus_util/seed_etl/README.md

Run examples
`python seed_etl/refresh_data.py`
"""

import pandas as pd
import logging
from locutus_util.helpers import logger, read_file, parse_owl2_data
from locutus_util.common import SEED_ETL_DIR


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_csv(source_data, output_file, mapping_config):
    """
    Transforms a source data into the desired final schema based on the given mapping configuration(seed_config.yaml).
    Saves the data in the data dir as csv.
    """
    try:

        final_schema = [
            "code", "system", "display", "description",
            "terminology_id", "terminology_description", "terminology_name", "terminology_resource_type"
        ]
        
        transformed_rows = []
        for _, row in source_data.iterrows():
            transformed_row = {}
            for final_column in final_schema:
                if final_column in mapping_config:
                    mapping_details = mapping_config.get(final_column)
                    if 'value' in mapping_details:
                        transformed_row[final_column] = mapping_details.get('value')

                    elif 'source_column' in mapping_details:
                        source_column = mapping_details.get('source_column')
                        transformed_row[final_column] = row[source_column]

            transformed_rows.append(transformed_row)

    except Exception as e:
        logger.error(f"Error processing file {output_file}: {e}")

    transformed_data = pd.DataFrame(transformed_rows, columns=final_schema)
    formatted_data = transformed_data.sort_values(by=['code','display']).drop_duplicates(keep='first')
    formatted_data.to_csv(output_file, index=False)
    logger.debug(f"Transformed data saved to {output_file}")

def transform_owl(source_data, output_file, mapping_config):
    """
    Transforms a source data into the desired final schema based on the given mapping configuration(seed_config.yaml).
    Saves the data in the data dir as csv.
    """
    try:

        final_schema = [
            "code", "system", "display", "description",
            "terminology_id", "terminology_description", "terminology_name", "terminology_resource_type"
        ]
        
        transformed_rows = []
        for _, row in source_data.iterrows():
            transformed_row = {}
            for final_column in final_schema:
                if final_column in mapping_config:
                    mapping_details = mapping_config.get(final_column)
                    if 'value' in mapping_details:
                        transformed_row[final_column] = mapping_details.get('value')

                    elif 'source_column' in mapping_details:
                        source_column = mapping_details.get('source_column')
                        transformed_row[final_column] = row[source_column]

            transformed_rows.append(transformed_row)

    except Exception as e:
        logger.error(f"Error processing file {output_file}: {e}")

    transformed_data = pd.DataFrame(transformed_rows, columns=final_schema)
    formatted_data = transformed_data.sort_values(by=['code','display']).drop_duplicates(keep='first')
    formatted_data.to_csv(output_file, index=False)
    logger.debug(f"Transformed data saved to {output_file}")

def process_files(file_metadata, input_dir, seeding_input_dir):
    """
    Set variables and run the transformation function.
    For src files that contain only one enumeration
    """
    try:
        source_data = file_metadata.get('source_data')
        norm_fns = file_metadata.get('normalized_data').get('name')

        input_file = input_dir / source_data.get('name')
        if source_data.get('type') == 'url':
            input_file = source_data.get('name')

        for file in norm_fns:
            output_file = seeding_input_dir / file

            source_data, file_ext = read_file(input_file, source_data.get('delimeter'))

            if file_ext == '.owl':
                source_data = parse_owl2_data(source_data)
            
            transform_csv(source_data, output_file, file_metadata.get('mappings'))
    except:
        logger.error(f"Could not process {file}")

def process_combined_files(file_metadata, input_dir, seeding_input_dir):
    """    
    Set variables and run the transformation function.
    For src files that contain many enumerations
    """

    source_data = file_metadata.get('source_data')
    mappings = file_metadata.get('mappings')      

    input_file = input_dir / source_data.get('name')
    if source_data.get('type') == 'url':
        input_file = mappings.get('name')

    source_data, file_ext = read_file(input_file, source_data.get('delimeter'))

    # Get the distinct variables from the src data
    t_column = mappings.get('tgt_variable')
    vars = source_data[t_column].drop_duplicates(keep='first')

    for var in vars:
        # Generate variable specific data for the transformation.
        name = f'acr-{var}'
        output_file = seeding_input_dir / f'{name}.csv'
        sep_data = source_data[source_data[t_column] == var].copy()
        sep_data['terminology_id'] = f'ftd-{name}'
        sep_data['terminology_name'] = name

        transform_csv(sep_data, output_file, mappings)

if __name__ == "__main__":
    logger.info('STARTED refreshing data.')

    config_file = SEED_ETL_DIR / "seed_config.yaml"
    config, file_ext = read_file(config_file)

    # Process each file in the config file
    for filename, file_metadata in config.items():
        # If the file does not need to be refreshed
        if not file_metadata.get('refresh_or_normalize') == True:
            logger.debug(f"Skipping inactive file: {filename}")
            continue
        # Process all active files containing a single variable
        if not file_metadata.get('combined_data'):
            process_files(file_metadata, SEED_ETL_DIR / 'refresh_src_data' , SEED_ETL_DIR)  
            logger.debug(f'Processing active file: {filename}')
        # Process all active files containing multiple variables
        if file_metadata.get('combined_data',False) == True:
            process_combined_files(file_metadata, SEED_ETL_DIR / 'refresh_src_data' , SEED_ETL_DIR)  
            logger.debug(f'Processing active combined file: {filename}')
    logger.info('COMPLETED refreshing data.')

