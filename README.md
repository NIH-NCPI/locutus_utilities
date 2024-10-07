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
[Here]("https://realpython.com/python-virtual-environments-a-primer/") for more on virtual environments.

    ```bash
    # Step 1: cd into the directory to store the venv

    # Step 2: run this code. It will create the virtual env named abacus_venv in the current directory.
    python3 -m venv abacus_venv

    # Step 3: run this code. It will activate the abacus_venv environment
    source abacus_venv/bin/activate # On Windows: venv\Scripts\activate

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
   * [run_ontology_api_etl](#run_ontology_api_etl) <br>
   * [drop_seed_data](#drop_seed_data) <br> 
   * [update_all_seed_data](#update_all_seed_data) <br>

## Commands
### run_ontology_api_etl 
This command will trigger the script that gathers ontology data from various
API sources and then stores the collected data in the firestore project defined
in the command arguments.
```bash
run_ontology_api_etl -p {Project_id}
```
### drop_seed_data
This command will trigger the script that deletes all data it defines as 
'seed data' from the firestore project defined in the command arguments.
```bash
drop_seed_data -p {Project_id}
```
### update_all_seed_data
This command will trigger all seed data scripts to run, therefore storing the
seed data into the firestore project defined in the command arguments. <br>
**Seed data scripts** : run_ontology_api_etl
```bash
update_all_seed_data -p {Project_id}
```

## Working on a branch?
    If working on a new feature it is possible to install a package version within
    the remote or local branch
      ```
    # remote
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git@{branch_name}

    # local
    pip install -e .
    ```