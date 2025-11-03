
## locutus_util/refresh_data.py
Overview:
- Pulls data from its external source when applicable. Uses the mappings contained in the `seed_config.yaml` to normalize the src data. Creates a normalized data csv for each Terminology that will be used to seed the database.
Uses:
- When external data needs to be pulled in, to refresh seed data. 
- When a flat file needs to be cleaned and normalized. 
Process:
- Make any necessary edits to `locutus_util/data/seed_etl/seed_config.yaml`. See the documentation on this file below for more information.
- From locutus_util run:  `python seed_etl/refresh_data.py`

## Seed the database
Overview:
- Formats normalized data into json to be used as the body of a request to 'locutus' to:<br> 1. Add the Terminology to the db or <br> 2. Delete codes from that Terminology in the db.
Process:
- Make any necessary edits to `locutus_util/data/seed_etl/seed_config.yaml`. See the documentation on this file below for more information.
- From locutus_util run:  `python seed_etl/seed_database.py -e {env} -a {action}`
  - `-e` - Base url of the db to be seeded.
  - `-a` - Action to perform. choices=['seed','delete']

## locutus_util/data/seed_etl/seed_config.yaml
- Defines metadata of the source seed data tables, and sources(when applicable). <br>
#### How to read/fill out the config file:
1. Each file should have its own object in the config file.
Naming convention: Name it what the Terminology id is to be, for example `ftd-acr-enum-relationship-code`
2. The next few attributes control how the data is used.
```bash
refresh_or_normalize: False
# Flag used to determine if 'refresh_data.py' should run on this data. Answers the question. 'Does the data need to be refreshed from its source, or reformatted in some way?'. 

# Options [True,False]


---------------------------------
seed_db: False

# Flag used to determine if 'seed_db.py' should run its 'seed' action on this data. Answers the question. 'Does the data need to seed or re-seed the database?'. 

# Options [True,False]


---------------------------------
remove_codes: False

# Flag used to determine if 'seed_db.py' should run its 'delete' action on this data. Answers the question. 'Is there something wrong with the data that was seeded previously for this Terminology?'. 

# Options [True,False]


--------------------------------
combined_data: True

# Optional flag to mark src files that hold multiple Terminologies worth of data to be normalized or seeded.

# Options [True,False]
```

3. The next attribute defines the source data, used for reading in the data prior to processing it. 
```bash
source_data:
# This attribute could be set to 'None' if the associated data is already in a format that can be seeded. For example, see concept_map_relationship in the yaml file.

    type: file
    # Flags the data as being a static file found in the data directory, or if the data is read in using a URL.
    #Options [file, url]

    name: "pedigree_family_history_terminology.owl"
    # Name of the file in the data/seed_etl directory, or the url of the source file.
    #Options [file, url]


    delimeter: None
    # Delimeter used in the source file. \
    # .owl files should be `None`
    # Options [None, "," , "/t"]

```
4. The next attribute defines the normalized/clean data, ready for seeding. Used to create a clean file (refresh_data.py) and when seeding the db (seed_db.py).
```bash
normalized_data:

    type: csv
    # Flags the data as being a static file found in the data directory, or if the data is read in using a URL.
    #Options [file, url]

    name: 
      - "ftd-acr-enum-relationship-code.csv"
    # Name of the file in the data/seed_etl directory, or the url of the source file.
    #Options [file, url]

    delimeter: None
    # Delimeter used in the source file. \
    # .owl files should be `None`
    # Options [None, "," , "/t"]

```
4. The next attribute will allow pulling data from the normalized files, as well as the ability to define data that isn't in the source data and can be hardcoded.
```bash
  mappings: 
  # These map src data to normalize the src data into the format necessary for a Terminology to be imported into the db. 
  # 'source_column' is used when the src data has a column that should be used to populate the field.
  # 'value' is used when the column will be hardcoded across the Terminology.
    
    tgt_variable: enumeration_group 
    # Optional: Used if the src data is 'combined_data'. This defines the column to split the src data by, to create separate files for seeding.

    code:
      source_column: code

    system:
      value: "http://purl.org/ga4gh/kin.owl"

    display:
      source_column: "display"

    description:
      source_column: "description"

    terminology_id:
      value: "ftd-acr-enum-relationship-code"
      # Prefixing the terminology_id with ftd will make them easier to find in the db.
      # If they are specifically mentioned in the tgt/harmonized model include a model identifier(acr) to flag them.

    terminology_description:
      value: "The Kinship Ontology (KIN) is a family relations ontology developed as part of the Global Alliance for Genomics and Health Pedigree Standard project."

    terminology_name:
      value: "Kinship Ontology (KIN)"

    terminology_resource_type:
      value: "Terminology"
```

## Seeding a database with existing seed data.
Data that has been previously used to seed a database will already have a properly formatted csv. 
1. Edit `locutus_util/data/seed_etl/seed_config.yaml`. Ensure 'seed_db' is set to True for data to be imported into the db, and False for those that shouldn't be seeded. No other changes necessary.
2. Run `locutus_util/seed_etl/seed_data.py -e {env}` as explained above to seed the database.

## Refreshing data from an external source, formatting, then seeding the db
Some source files can be updated automatically by accessing an external source file. These will be configured to have the 'source_data: {type: url}', and a url as the 'source_data name'. The static 'source_data: {type: file}' files require manual updates prior to seeding.
1. Edit `locutus_util/data/seed_etl/seed_config.yaml`. Ensure 'refresh_or_normalize' is set to True for data to be refreshed, and formatted. Ensure 'seed_db' is set to True for data to be imported into the db.
2. Run `locutus_util/seed_etl/refresh_data.py` as explained above to format the data.
3. Run `locutus_util/seed_etl/seed_data.py -e {env}` as explained above to seed the database.

## Deleting codes from seeded Terminologies
1. Edit `locutus_util/data/seed_etl/seed_config.yaml`. Ensure 'remove_codes' is set to True for data requiring deletions.
2. Run `locutus_util/seed_etl/seed_data.py -e {env} -a delete` as explained above to delete codes from the configured Terminology.

## Adding new source data to the process.

### For *unformatted* local flat files, or external files (.owl, single variable .csvs, and multiple variable .csvs(ftd-acr-tgt-enums)) 
1. Add another object to `locutus_util/data/seed_etl/seed_config.yaml`. Define the metadata as explained above.
2. Run `locutus_util/seed_etl/refresh_data.py` as explained above to format the data.
3. Run `locutus_util/seed_etl/seed_data.py` as explained above to seed the database.

### For *formatted* local flat files, or external files (.owl, single variable .csvs, and multiple variable .csvs(ftd-acr-tgt-enums)) 
1. Add another object to `locutus_util/data/seed_etl/seed_config.yaml`. Define the metadata as explained above.
2. Run `locutus_util/seed_etl/seed_data.py` as explained above to seed the database.
