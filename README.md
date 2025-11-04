# Locutus Utilities

## Overview

The `locutus_utilities` repository includes scripts and tools that facilitate the development and maintenance of [Locutus](https://github.com/NIH-NCPI/locutus). These utilities may include automation tools, and other resources that support the application's lifecycle.


## Package install
```bash
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git
```


 ## Commands   

 Available commands:
   * [sideload_run](#sideload_run) <br>
   * [seed_data](#seed_data) <br>

### sideload_run 
### mapping_loader_table.py
Map existing `Table.variables` to the `mappings` specified in a csv. <br>
Prior to running this script, the user should check with the 'locutus' dev team, for any recent updates to the mapping process. <br>
Expected csv formatting seen below. This file should be placed in the data/input/sideload_data directory.<br>
```csv
source_variable,source_enumeration,code,display,system,provenance,comment
case_control_aaa,C99269,233985008,Abdominal aortic aneurysm,SNOMED,RJC,
```

```bash
# run command
sideload_run -e {environment} -p {project_id} -f data/input/sideload_data/{filename}.csv -t {db table id}

* -e, --env
    * Description: Choose the environment that the table is within.
    * choices=["DEV", "UAT", "ALPHA", "PROD"]
    * Required: False
* -p, --project_id
    * Description: Choose the environment that the table is within.
    * Required: True
* -f, --file
    * Description: The FILEPATH of the file containing the mappings. Recommended to store within the sideload_data dir, for ease of use.
    * Required: True
* -t, --table
    * Description: The table_id that the mappings belong to. 'tb*' format
    * Required: True     
```


### seed_data
```bash 
# run command
seed_data -e {env} -a {action}

* -e --env
    * Description: Will be used as the base url in an api request to locutus.
    * Required: False
    * Default: http://localhost:8080
* -a, --action
    * Description: Choose whether to seed the db with a Terminology, or delete codes from a db Terminology.
    * Required: False
    * Default: 'seed' 
    * Options: ['seed', 'delete']

- Developers, to add new seed data, or refresh existing data from external sources, refer to `locutus_util/seed_etl/README.md`.
```


# Developer Notes

## Prerequisites to run locutus_utilities scripts locally
* Install **Google Cloud SDK**: Installed and authenticated to use Google Cloud services.
* Install **setuptools**
* A UMLS api key is required to retrieve any results from the UMLS endpoint. If you don't already have one, log in and request an API key from [UMLS](https://uts.nlm.nih.gov/uts/). When you have this you can create a environment variable with the code below. 
```bash
export UMLS_API_KEY=your_actual_umls_api_key
```
* Install the package and dependencies from the root directory.

    ```bash
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git

    pip install -r requirements.txt
    ```


## Installation methods:
```bash
# Search-dragon should installed using the following command.
pip install git+https://github.com/NIH-NCPI/locutus_utilities.git

# This install command will ensure the proper version installed. Useful for troubleshooting purposes.
pip install --force-reinstall --no-cache-dir git+https://github.com/NIH-NCPI/locutus_utilities.git

# Installing a specific branch of locutus_utilities.
pip install git+https://github.com/NIH-NCPI/locutus_utilities.git@{branch_name}

# Use this method for local development. In the root dir of the cloned repo run this command to enact local changes. 
pip install -e .
```