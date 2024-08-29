"""
Gathers metadata of ontologies found in the OLS api and adds any ontologies 
necessary that are not included in ols.
Jira ticket FD-1381
"""

import requests
import pandas as pd
import sys
import os

# Specify the path to resources
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from locutus_util.resources import ONTOLOGY_API_LOOKUP_TABLE_PATH, OLS_API_BASE_URL, MONARCH_API_BASE_URL, LOINC_API_BASE_URL


class OntologyMetadataCollector:
    def __init__(self):
        self.ols_ontologies_url = f"{OLS_API_BASE_URL}ontologies"
        self.extracted_data = []

    def fetch_data(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None
        
    def collect_ols_data(self):
        # Fetch the first page of data
        print("Fetching data")
        data = self.fetch_data(self.ols_ontologies_url)
        # Loop through the pages until there are no more pages left
        print("Transforming data")

        while data:
            ontologies = data['_embedded']['ontologies']
            for ontology in ontologies:
                config = ontology.get('config', {})
                # Check for required fields
                required_fields = []
                for field in required_fields:
                    if not config[field]:
                        raise ValueError(f"Required field '{field}' is missing from ontology:{ontology['ontologyId']}.")
            
                self.extracted_data.append({
                    'api_url': OLS_API_BASE_URL,
                    'api_id': 'ols',
                    'ontology_code': ontology['ontologyId'],
                    'curie': config.get('preferredPrefix', ''),
                    'ontology_title': config.get('title', ''),
                    'system': config.get('fileLocation', ''),
                    'version': config.get('versionIri', '')
                })
            # Check if there is a next page
            if '_links' in data and 'next' in data['_links']:
                next_url = data['_links']['next']['href']
                data = self.fetch_data(next_url)
            else:
                break

        return self.extracted_data
        

    def add_manual_ontologies(self):
        # Add one-off ontologies FD-1381
        # TODO: If possible eventually remove the hard code.
        manual_addition_ontologies = [
            [MONARCH_API_BASE_URL, "monarch", "Environmental Conditions, Treatments and Exposures Ontology", "ecto", "ECTO", "http://purl.obolibrary.org/obo/ecto.owl", ""],
            [LOINC_API_BASE_URL, "loinc", "Logical Observation Identifiers, Names and Codes (LOINC)", "loinc", "", "http://loinc.org", ""]
        ]
        return pd.DataFrame(manual_addition_ontologies, columns=self.get_column_names())

    def get_column_names(self):
            return ["api_url", "api_id", "ontology_title", "ontology_code", "curie", "system", "version"]

    def ontologies_to_csv(self):
        ols_data = self.collect_ols_data()
        df = pd.DataFrame(ols_data, columns=self.get_column_names())
        additional_df = self.add_manual_ontologies()
        print(f"Adding hard coded ontologies count:{len(additional_df)}")
        df = pd.concat([df, additional_df], ignore_index=True)

        df.to_csv(ONTOLOGY_API_LOOKUP_TABLE_PATH, index=False)
        print(f"{len(df)} ontologies saved to ontology_definition.csv")


if __name__ == "__main__":
    collector = OntologyMetadataCollector()
    collector.ontologies_to_csv()