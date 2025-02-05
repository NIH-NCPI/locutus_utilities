# Locutus Utilities

## Overview

The `locutus_utilities` repository includes scripts and tools that facilitate the development and maintenance of [Locutus](https://github.com/NIH-NCPI/locutus). These utilities may include automation tools, and other resources that support the application's lifecycle.


## Prerequisites

1. **Google Cloud SDK**: Installed and authenticated to use Google Cloud services.
2. **Firestore** enabled in your Google Cloud project.
3. Install **setuptools**
4. If running the 'update_ontology_api' option, You'll need a UMLS api key. If you don't already have one, log in and request an API key from [UMLS](https://uts.nlm.nih.gov/uts/). When you have this you can create a environment variable with the code below. 
```bash
export UMLS_API_KEY=your_actual_umls_api_key
```

## Installation

## Installation

1. **Create and activate a virtual environment** (recommended):<br>
[[Click here]]("https://realpython.com/python-virtual-environments-a-primer/") for more on virtual environments.

    ```bash
    # Step 1: cd into the directory to store the venv

    # Step 2: run this code. It will create the virtual env named utils_venv in the current directory.
    python3 -m venv utils_venv

    # Step 3: run this code. It will activate the utils_venv environment
    source utils_venv/bin/activate # On Windows: venv\Scripts\activate

    # You are ready for installations! 
    # If you want to deactivate the venv run:
    deactivate
    ```

2. **Install the package and dependencies from the root directory.**:
    ```bash
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git

    pip install -r requirements.txt
    ```
3. **Run a command/action**

   ## Available actions:
   * [utils_run](#utils_run) <br>
   * [sideload_run](#sideload_run) <br>

## Commands
### utils_run 
## usage 
```bash
utils_run -p <project_id> -o <option> -a <action>
```
* -p, --project
    * Description: GCP Project to edit.
    * Required: Yes

* -o, --option
    * Description: Choose the operation to perform.
    * Choices:
        * `update_ontology_api`: Updates the ontology API in Firestore.
        * `update_seed_data`: Updates seed data in Firestore.
        * `delete_project_data`: Deletes all data from the Firestore database.
        * `reset_database`: Deletes all data, then reseeds the Firestore database.
    * Required: Yes

* -a, --action
    * Description: Specify the action to take. Only used when running `update_ontology_api`, or `reset_database`
    * Choices:
        * `upload_from_csv`: Upload data from an existing CSV file to Firestore.
        * `update_csv`: Fetch data from APIs and update the CSV file only.
        * `fetch_and_upload`: Fetch data from APIs and upload it to Firestore.
    * Default: `upload_from_csv`
    * Required: No 

* -u, --which_ontologies
    * Description: Choose to include all ontologies or only a selection. Only used when running `update_ontology_api`, or `reset_database`
    * Choices:
        * `curated_ontologies_only`: Use the selected default ontologies.
        * `all_ontologies`: Use all ontologies.
    * Default: `all_ontologies`

### sideload_run 
### mapping_loader_table.py
Map existing `Table.variables` to the `mappings` specified in a csv. <br>
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
    * Description: Choose the operation to perform.    
    * Required: True
* -t, --table
    * Description: The table_id that the mappings belong to. 'tb*' format
    * Required: True     
```


## Working on a branch?
    If working on a new feature it is possible to install a package version within
    the remote or local branch
      ```
    # remote
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git@{branch_name}

    # If using the command above, you may need to force a reinstallation to ensure the latest version.
    pip install --force-reinstall --no-cache-dir git+https://github.com/NIH-NCPI/locutus_utilities.git

    # local - if working on the package the installation will automatically update
    pip install -e .

    ```