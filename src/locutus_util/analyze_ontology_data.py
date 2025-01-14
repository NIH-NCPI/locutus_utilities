"""
Gathers metadata of ontologies found in the external apis for analysis.

Returns the summary csvs in the locutus_utilities.data.logs directory

Jira ticket FD-1381
"""

import requests
import pandas as pd
from datetime import date
from locutus_util.ontology_api_etl import (
    collect_ols_data,
    collect_umls_data,
)
from locutus_util.common import LOGS_PATH

JIRA_ISSUES = ["fd1381", "fd1653"]
export_date = date.today()

ols_data = collect_ols_data()
umls_data = collect_umls_data()

# Define columns to export
column_names = [
    "api_url",
    "api_id",
    "api_name",
    "ontology_title",
    "ontology_code",
    "curie",
    "system",
    "version",
    "ontology_family",
]

# Add one-off ontologies FD-1381
# TODO: If possible eventually remove the hard code.
manual_addition_ontologies = [
    [
        "",
        "Manual addition",
        "Manual addition",
        "Environmental Conditions, Treatments and Exposures Ontology",
        "ecto",
        "ECTO",
        "http://purl.obolibrary.org/obo/ecto.owl",
        "",
        "",
    ],
    [
        "",
        "Manual addition",
        "Manual addition",
        "Logical Observation Identifiers, Names and Codes (LOINC)",
        "loinc",
        "LOINC",
        "http://loinc.org",
        "",
        "",
    ],
]
# Create a DataFrames with the requested ontologies
ols_df = pd.DataFrame(ols_data, columns=column_names)
umls_df = pd.DataFrame(umls_data, columns=column_names)
additional_df = pd.DataFrame(manual_addition_ontologies, columns=column_names)

# Concatenate the api sourced ontologies with the manually added ontologies.
print(f"Adding hard coded ontologies count:{len(manual_addition_ontologies)}")
df = pd.concat([ols_df, umls_df, additional_df], ignore_index=True)
df = df.sort_values(by=["curie", "api_id"], ascending=True, ignore_index=True)

# Save the DataFrame to a CSV file
df.to_csv(f"{LOGS_PATH}/ontology_definition_{export_date}.csv", index=False)

print(f"{len(df)} ontologies saved to ontology_definition_{export_date}.csv")


def format_ontology_data(ols_df, umls_df, additional_df):
    """
    Format the data to include columns for OLS, UMLS, Manual Addition (with their systems),
    and an ontology_family column using coalesce logic.
    """
    # Combine unique 'curie' values from all data sources
    combined_df = pd.concat(
        [ols_df[["curie"]], umls_df[["curie"]], additional_df[["curie"]]],
        ignore_index=True,
    )
    combined_df = combined_df.drop_duplicates(subset="curie").reset_index(drop=True)

    # Map the 'system' column from each data source
    ols_system = ols_df.drop_duplicates(subset="curie").set_index("curie")["system"]
    ols_system = ols_system.apply(lambda x: x if pd.notna(x) else "Present but no system defined")
    umls_system = umls_df.drop_duplicates(subset="curie").set_index("curie")["system"]
    umls_system = umls_system.apply(lambda x: x if pd.notna(x) else "Present but no system defined")
    manual_system = additional_df.drop_duplicates(subset="curie").set_index("curie")[
        "system"
    ]
    manual_system = manual_system.apply(lambda x: x if pd.notna(x) else "Present but no system defined")

    # Map the 'ontology_family' column from each data source
    ols_family = ols_df.drop_duplicates(subset="curie").set_index("curie")[
        "ontology_family"
    ]
    umls_family = umls_df.drop_duplicates(subset="curie").set_index("curie")[
        "ontology_family"
    ]
    manual_family = additional_df.drop_duplicates(subset="curie").set_index("curie")[
        "ontology_family"
    ]

    # Add the columns to the combined DataFrame
    combined_df["ols"] = combined_df["curie"].map(ols_system)
    combined_df["umls"] = combined_df["curie"].map(umls_system)
    combined_df["manual_addition"] = combined_df["curie"].map(manual_system)

    # Add the 'ontology_family' column using coalesce logic
    combined_df["ontology_family"] = (
        combined_df["curie"]
        .map(ols_family)
        .fillna(combined_df["curie"].map(manual_family))
        .fillna(combined_df["curie"].map(umls_family))
    )
    combined_df = combined_df.sort_values(
        by=["curie"], ascending=True, ignore_index=True
    )
    return combined_df


formatted_df = format_ontology_data(ols_df, umls_df, additional_df)

# Save to CSV if needed
formatted_df.to_csv(
    f"{LOGS_PATH}/formatted_ontology_data_{export_date}.csv", index=False
)

print(f"Formatted data saved to formatted_ontology_data_{export_date}.csv")
