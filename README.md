# Locutus Utilities

## Overview

The `locutus_utilities` repository includes scripts and tools that facilitate the development and maintenance of [Locutus]("https://github.com/NIH-NCPI/locutus"). These utilities may include automation tools, and other resources that support the application's lifecycle.


## Prerequisites

1. **Google Cloud SDK**: Installed and authenticated to use Google Cloud services.
2. **Firestore** enabled in your Google Cloud project.

## Installation

1. **Create and activate a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate 
    # On Windows: venv\Scripts\activate
    ```

2. **Install the package and dependencies**:
    ```bash
    pip install git+https://github.com/NIH-NCPI/locutus_utilities.git
    ```

3. **Set up Google Cloud credentials**:
   Ensure that your Google Cloud credentials are correctly set up. You can authenticate and check your configuration using the following commands:
   ```bash
   gcloud auth application-default login

   gcloud config list
   ```