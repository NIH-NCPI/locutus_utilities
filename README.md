# Locutus Utilities

## Overview

The `locutus_utilities` repository includes scripts and tools that facilitate the development and maintenance of [Locutus]("https://github.com/NIH-NCPI/locutus"). These utilities may include automation tools, and other resources that support the application's lifecycle.


## Prerequisites

1. **Google Cloud SDK**: Installed and authenticated to use Google Cloud services.
2. **Firestore** enabled in your Google Cloud project.
3. Install **setuptools**

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

2. **Install the package and dependencies**:
    ```bash
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git
    ```
3. **Run a command/action**

   ## Available actions:
   * [utils_run](#utils_run) <br>

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
    * Description: Specify the action to take.
    * Choices:
        * `upload_from_csv`: Upload data from an existing CSV file to Firestore.
        * `update_csv`: Fetch data from APIs and update the CSV file only.
        * `fetch_and_upload`: Fetch data from APIs and upload it to Firestore.
    * Default: `upload_from_csv`

## Working on a branch?
    If working on a new feature it is possible to install a package version within
    the remote or local branch
      ```
    # remote
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git@{branch_name}

    # local
    pip install -e .
    ```