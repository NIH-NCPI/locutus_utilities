Review the root dir README.md for setup and run instructions
Review the data/input/ontology_data README.md for more about the files found in the directory.

# To add ontologies to the firestore OntologyAPI Collection

1. Update data/input/ontology_data/manual_ontology_transformations.csv with the new changes/ontologies. Make sure the google sheet is also up to date.
- [google sheet](https://docs.google.com/spreadsheets/d/1Fq94B47ZR1Gz6p48SI9T_WGizOmyi5lYEDRZ1KpY42s/edit?gid=1963780454#gid=1963780454) 

2. Update data/input/ontology_data/included_ontologies with the new changes/ontologies.
- 

Run utils_run -p locutus-dev -o update_ontology_api -a update_csv

Look over the updates made to data/input/ontology_data/ontology_api. The data in this file will be the source of truth for the data in the Firestore collection. However, only the ones listed in the data/input/ontology_data/inluded_ontologies.csv will be included in the import.

Once the changes are confirmed run utils_run -p locutus-dev -o update_ontology_api -a upload_from_csv
