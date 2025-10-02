# Locutus Utilities

## Overview

The `locutus_utilities` repository includes scripts and tools that facilitate the development and maintenance of [Locutus](https://github.com/NIH-NCPI/locutus). These utilities may include automation tools, and other resources that support the application's lifecycle.


## Prerequisites

1. **Google Cloud SDK**: Installed and authenticated to use Google Cloud services.
  * [[Click here]](https://cloud.google.com/sdk/docs/install-sdk) for installation
  * [[Click here]](https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login) for authentication

```bash 
# Handy commands when working with gcloud

# Take a look at your current configuration
gcloud config list

# Set the project in the config. This package will set this for you when you run commands. There is no need to do so before running commands.
gcloud config set project {project-id}

# Recommended login if any scripts require reading from google sheets.
# If not reading from sheets, don't include the --scopes part of the command. See link above for more info. 
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/spreadsheets.readonly,https://www.googleapis.com/auth/drive.readonly

```
2. **Firestore** enabled in your Google Cloud project.
3. Install **setuptools**
4. If running the 'update_ontology_api' option, You'll need a UMLS api key. If you don't already have one, log in and request an API key from [UMLS](https://uts.nlm.nih.gov/uts/). When you have this you can create a environment variable with the code below. 
```bash
export UMLS_API_KEY=your_actual_umls_api_key
```

## Installation

## Installation

1. **Create and activate a virtual environment** (recommended):<br>
[[Click here]](https://realpython.com/python-virtual-environments-a-primer/) for more on virtual environments.

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
    pip install --force-reinstall --no-cache-dir git+https://github.com/NIH-NCPI/locutus_utilities.git

    # Using '--force-reinstall --no-cache-dir' will install the most recent versions. 
    pip install --force-reinstall --no-cache-dir -r requirements.txt
    ```
3. **Run a command/action**

   ## Available actions:
   * [utils_run](#utils_run) <br>
   * [sideload_run](#sideload_run) <br>

## Commands
### utils_run 
## usage 
```bash
utils_run -p <project_id> -o <option> -a <action> -w <which_ontologies>
```
* -p, --project
    * Description: GCP Project to edit.
    * Required: Yes

* -o, --option
    * Description: Choose the operation to perform.
    * Choices:
        * `update_ontology_api`: Updates the ontologyAPI Collection in Firestore.
        * `update_seed_data`: Updates seed data(Manually added Terminologies) in Firestore.
        * `delete_project_data`: Deletes all data from the Firestore database.
        * `reset_database`: Deletes all data, then reseeds the Firestore database.
    * Required: Yes

* -a, --action
    * Description: Specify the action to take. Only used when running `update_ontology_api`, or `reset_database`
    * Choices:
        * `upload_from_csv`: Upload data ontology_api.csv to Firestore. No update of the csv prior to upload.
        * `update_csv`: Fetch data from Ontology APIs(OLS,UMLS) and update the ontology_api.csv. No upload to Firestore.
        * `fetch_and_upload`: Fetch data from Ontology APIs(OLS,UMLS) and update the ontology_api.csv. Upload this into the Firestore.
    * Default: `upload_from_csv`
    * Required: No 

* -w, --which_ontologies
    * Description: Choose to include all ontologies or only a selection. Only used when running `update_ontology_api`, or `reset_database`. The curated list of ontologies are in data/input/ontology_data/included_ontologies.csv.
    * Choices:
        * `curated_ontologies_only`: Use the curated list of ontologies to populate the OntologyAPI Collection
        * `all_ontologies`: Use all available ontologies to populate the OntologyAPI Collection.
    * Default: `all_ontologies`

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