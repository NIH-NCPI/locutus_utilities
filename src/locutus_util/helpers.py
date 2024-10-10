import subprocess
from google.cloud import firestore
import time

def update_gcloud_project(project_id):
    """Update the active Google Cloud project."""
    command = ["gcloud", "config", "set", "project", project_id]
    
    try:
        print(f"Updating Google Cloud project to: {project_id}")
        subprocess.run(command, check=True)
        print(f"Project updated successfully. {project_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error updating project: {e}")


def delete_document(collection_name, document_id):
    """Delete a document and any docuements in their subcollections(removes the 
    subcollection), recursively."""
    db = firestore.Client()
    doc_ref = db.collection(collection_name).document(document_id)

    # Iterate through all subcollections of the document
    for subcollection in doc_ref.collections():
        subcollection_name = subcollection.id
        print(f"Deleting subcollection '{subcollection_name}' for document '{document_id}'.")

        # Delete the subcollection documents
        for subdoc in subcollection.stream():
            print(f"Deleting subdocument '{subdoc.id}' from subcollection '{subcollection_name}'.")
            delete_document(f"{collection_name}/{document_id}/{subcollection_name}", subdoc.id)
            
    # Delete the document itself
    doc_ref.delete()
    print(f"Deleted document {document_id} from collection {collection_name}.")

def delete_collection(collection_name):
    """Delete all documents in a collection(removes the collection), including 
    their sub-files(subcollections and their documents)."""
    db = firestore.Client()
    collection_ref = db.collection(collection_name)

    start_time = time.time()
    time_limit = 60

    # Loop until no documents are left
    while True:
        # Break loop if process takes longer than a minute
        if time.time() - start_time > time_limit:
            print("Exiting loop due to time limit.")
            break

        docs = collection_ref.stream()
        doc_count = 0

        for doc in docs:
            delete_document(collection_name, doc.id)
            doc_count += 1

        if doc_count == 0:
            print(f"Collection '{collection_name}' is now empty.")
            break
        else:
            print(f"Deleted {doc_count} documents from collection '{collection_name}'.")
