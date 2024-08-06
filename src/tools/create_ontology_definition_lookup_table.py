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

JIRA_ISSUES = ["fd1381"]

# Define the api endpoints used to request ontologies
ols_ontologies_url = f"{OLS_API_BASE_URL}ontologies"

# Initialize an empty list to store the extracted data
extracted_data = []

# Function to fetch data from a given URL
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None
    

# Fetch the first page of data
print("Fetching data")
data = fetch_data(ols_ontologies_url)
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
            
        extracted_data.append({
            'api_url': OLS_API_BASE_URL,
            'api_source': 'ols',
            'ontology_code': ontology['ontologyId'],
            'curie': config.get('preferredPrefix', ''),
            'ontology_title': config.get('title', ''),
            'system': config.get('fileLocation', ''),
            'version': config.get('versionIri', '')
        })
    # Check if there is a next page
    if '_links' in data and 'next' in data['_links']:
        next_url = data['_links']['next']['href']
        data = fetch_data(next_url)
    else:
        break

# Define columns to export
column_names = ["api_url", "api_source", "ontology_title", "ontology_code", "curie", "system", "version"]

# Create a DataFrame with the requested ontologies
df = pd.DataFrame(extracted_data, columns=column_names)

# Add one-off ontologies FD-1381
# TODO: If possible eventually remove the hard code.
manual_addition_ontologies = [
    [MONARCH_API_BASE_URL, "monarch", "Environmental Conditions, Treatments and Exposures Ontology", "ecto", "ECTO", "http://purl.obolibrary.org/obo/ecto.owl", ""],
    [LOINC_API_BASE_URL, "loinc", "Logical Observation Identifiers, Names and Codes (LOINC)", "loinc", "", "http://loinc.org", ""]
]

# Convert new data to DataFrame
additional_df = pd.DataFrame(manual_addition_ontologies, columns=column_names)

# Concatenate the api sourced ontologies with the manually added ontologies.
print(f"Adding hard coded ontologies count:{len(manual_addition_ontologies)}")
df = pd.concat([df, additional_df], ignore_index=True)

# Save the DataFrame to a CSV file
df.to_csv(ONTOLOGY_API_LOOKUP_TABLE_PATH, index=False)

print(f"{len(df)} ontologies saved to ontology_definition.csv")

