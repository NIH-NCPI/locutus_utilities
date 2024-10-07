import subprocess
from google.cloud import firestore

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
    """Delete a document and all its subcollections recursively."""
    db = firestore.Client()
    doc_ref = db.collection(collection_name).document(document_id)

    # Check if the document exists
    if not doc_ref.get().exists:
        print(f"Document '{document_id}' does not exist in collection '{collection_name}'.")
        return

    # Iterate through all subcollections of the document
    for subcollection in doc_ref.collections():
        # Recursively delete each document in the subcollection
        for subdoc in subcollection.stream():
            delete_document(subcollection.id, subdoc.id)  # Recursively delete subdocuments

    # Delete the document itself
    doc_ref.delete()
    print(f"Deleted document {document_id} from collection {collection_name}.")

def delete_collection(collection_name):
    """Delete all documents in a collection, including their subcollections."""
    db = firestore.Client()
    collection_ref = db.collection(collection_name)

    # Loop until no documents are left
    while True:
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
