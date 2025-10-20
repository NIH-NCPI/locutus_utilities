Review the root dir README.md for setup and run instructions
Review the data/input/ontology_data README.md for more about the files found in the directory.

# To add/edit ontologies in the firestore OntologyAPI Collection
1. Update data/input/ontology_data/included_ontologies with the new changes/ontologies.
2. Run `utils_run -p locutus-dev -o update_ontology_api -a update_csv`
3. Look at the changes that were made to `data/output/ontology_api_metadata.csv`
- If the changes to the file seem acceptable, no other edits are necessary. Skip to step 5.
- If the system was missing, or incorrect, continue with step 4.
4. Update data/input/ontology_data/manual_ontology_transformations.csv with the new changes/ontologies. Make sure the google sheet is also up to date.
- This file is used to overwrite systems, and prefixes
- [google sheet](https://docs.google.com/spreadsheets/d/1Fq94B47ZR1Gz6p48SI9T_WGizOmyi5lYEDRZ1KpY42s/edit?gid=1963780454#gid=1963780454) 
- Once updated, return to step 2.
5. `data/output/ontology_api_metadata.csv` should have been updated to reflect the future state of the OntologyAPI collection. Share the link to the changes in a PR for review.
6. Once approved, run `utils_run -p locutus-dev -o update_ontology_api -a upload_from_csv` to send the data from the csv to the Firestore.
 - TODO swap order, have reorg_for_firestore use data/output/ontology_api_metadata.csv as input. 
 - Make upload_from_csv run the reorg and push to FS only. No regeneration.
7. Check the Firestore and MD(after deploy/restart) for the changes.
