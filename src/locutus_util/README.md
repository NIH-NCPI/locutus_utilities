Review the root dir README.md for setup and run instructions
Review the data/input/ontology_data README.md for more about the files found in the directory.

# To add/edit ontologies in the firestore OntologyAPI Collection
1. Update data/input/ontology_data/included_ontologies with the new changes/ontologies.
2. Run `utils_run -p locutus-dev -o update_ontology_api -a update_csv`
3. Look at the changes that were made to data/input/ontology_data/ontology_api.csv
- Look over the updates made to data/input/ontology_data/ontology_api. The data in this file will be the source of truth for the data in the Firestore collection. However, only the ones listed in the data/input/ontology_data/inluded_ontologies.csv will be included in the Firestore import.
- If the system that was retrieved, from ols or umls, for the new ontology is acceptable no other edits are necessary. Look at any other changes to that csv and make sure no important systems were changed, revert if necessary. Once the systems look acceptable, skip to step 5.
- If the system was missing, or incorrect, continue with step 4.
4. Update data/input/ontology_data/manual_ontology_transformations.csv with the new changes/ontologies. Make sure the google sheet is also up to date.
- This file is used to overwrite systems, and prefixes
- [google sheet](https://docs.google.com/spreadsheets/d/1Fq94B47ZR1Gz6p48SI9T_WGizOmyi5lYEDRZ1KpY42s/edit?gid=1963780454#gid=1963780454) 
- Once updated, return to step 2.
5. Once everything looks good, run `utils_run -p locutus-dev -o update_ontology_api -a upload_from_csv` to check the output prior to running again in a prod env.
