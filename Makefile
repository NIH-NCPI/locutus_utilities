# Sets GCP project then runs seed data generation scripts.
update_all_seed_data:
	@if [ -z "$(PROJECT_ID)" ]; then \
		echo "Error: PROJECT_ID is not set."; \
		exit 1; \
	fi
	@python3 src/locutus_util/ontology_api_etl.py -p $(PROJECT_ID)

