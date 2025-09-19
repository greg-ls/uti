import sqlite3
import os
import logging
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

# Define database paths
DB_DIR = '/home/steeve/cv_format/data'
SQLITE_DB_PATH = os.path.join(DB_DIR, 'cv_metadata.db')
CHROMADB_PATH = os.path.join(DB_DIR, 'chroma_db')

class CVDatabase:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        self.conn = sqlite3.connect(SQLITE_DB_PATH)
        self.cursor = self.conn.cursor()
        self._init_sqlite_db()
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
        
        # Using a default embedding function for now.
        # In a real scenario, you might want to use a specific model (e.g., OpenAI, Sentence Transformers)
        # Ensure you have the necessary API keys or models installed for the chosen embedding function.
        # For demonstration, we'll use a basic one or assume it's configured externally.
        # If using OpenAI, you'd do:
        # from dotenv import load_dotenv
        # load_dotenv()
        # openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        #     api_key=os.environ.get("OPENAI_API_KEY"),
        #     model_name="text-embedding-ada-002"
        # )
        # self.cv_collection = self.chroma_client.get_or_create_collection(
        #     name="cv_embeddings",
        #     embedding_function=openai_ef
        # )
        # For now, let's use a dummy embedding function or rely on ChromaDB's default if available
        # or specify a model that can be run locally if no API key is provided.
        # For simplicity, we'll assume a default or a pre-configured one for now.
        # A more robust solution would involve checking for API keys or local model availability.
        
        # For now, let's create a collection without a specific embedding function,
        # assuming embeddings will be provided externally or a default will be used by ChromaDB.
        # This might need adjustment based on actual embedding generation.
        try:
            self.cv_collection = self.chroma_client.get_or_create_collection(name="cv_embeddings")
            logger.info("ChromaDB collection 'cv_embeddings' initialized.")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collection: {e}")
            # Fallback or raise error if ChromaDB cannot be initialized
            self.cv_collection = None


    def _init_sqlite_db(self):
        """Initializes the SQLite database schema."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_docx_path TEXT NOT NULL UNIQUE,
                markdown_path TEXT NOT NULL,
                extracted_text TEXT,
                availability_date TEXT,
                collaborator_wishes TEXT,
                upload_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        logger.info("SQLite database 'cv_data' table ensured.")

    def add_cv(self, original_docx_path, markdown_path, extracted_text, availability_date=None, collaborator_wishes=None):
        """
        Adds a new CV entry to SQLite and its text content to ChromaDB.
        Returns the ID of the newly added CV.
        """
        try:
            self.cursor.execute('''
                INSERT INTO cv_data (original_docx_path, markdown_path, extracted_text, availability_date, collaborator_wishes)
                VALUES (?, ?, ?, ?, ?)
            ''', (original_docx_path, markdown_path, extracted_text, availability_date, collaborator_wishes))
            self.conn.commit()
            cv_id = self.cursor.lastrowid
            logger.info(f"CV added to SQLite with ID: {cv_id}")

            if self.cv_collection and extracted_text:
                # Add document to ChromaDB. The ID in ChromaDB will be the SQLite CV ID.
                self.cv_collection.add(
                    documents=[extracted_text],
                    metadatas=[{"cv_id": cv_id, "original_docx_path": original_docx_path}],
                    ids=[str(cv_id)]
                )
                logger.info(f"CV content added to ChromaDB for ID: {cv_id}")
            return cv_id
        except sqlite3.IntegrityError:
            logger.warning(f"CV with original_docx_path '{original_docx_path}' already exists.")
            return None
        except Exception as e:
            logger.error(f"Error adding CV: {e}")
            return None

    def get_cv(self, cv_id=None, original_docx_path=None):
        """Retrieves a CV entry by ID or original_docx_path."""
        if cv_id:
            self.cursor.execute('SELECT * FROM cv_data WHERE id = ?', (cv_id,))
        elif original_docx_path:
            self.cursor.execute('SELECT * FROM cv_data WHERE original_docx_path = ?', (original_docx_path,))
        else:
            return None
        
        row = self.cursor.fetchone()
        if row:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, row))
        return None

    def update_cv(self, cv_id, availability_date=None, collaborator_wishes=None, extracted_text=None):
        """
        Updates an existing CV entry in SQLite.
        If extracted_text is provided, it also updates the ChromaDB entry.
        """
        try:
            update_fields = []
            update_values = []
            if availability_date is not None:
                update_fields.append('availability_date = ?')
                update_values.append(availability_date)
            if collaborator_wishes is not None:
                update_fields.append('collaborator_wishes = ?')
                update_values.append(collaborator_wishes)
            if extracted_text is not None:
                update_fields.append('extracted_text = ?')
                update_values.append(extracted_text)

            if not update_fields:
                logger.warning("No fields to update for CV ID: {cv_id}")
                return False

            query = f"UPDATE cv_data SET {', '.join(update_fields)} WHERE id = ?"
            update_values.append(cv_id)
            
            self.cursor.execute(query, tuple(update_values))
            self.conn.commit()
            logger.info(f"CV with ID {cv_id} updated in SQLite.")

            if self.cv_collection and extracted_text is not None:
                # Update document in ChromaDB (delete and re-add for simplicity, or use update if available)
                # ChromaDB's update method for documents is more complex, re-adding is simpler for full content change
                self.cv_collection.delete(ids=[str(cv_id)])
                self.cv_collection.add(
                    documents=[extracted_text],
                    metadatas=[{"cv_id": cv_id, "original_docx_path": self.get_cv(cv_id)['original_docx_path']}],
                    ids=[str(cv_id)]
                )
                logger.info(f"CV content updated in ChromaDB for ID: {cv_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating CV with ID {cv_id}: {e}")
            return False

    def delete_cv(self, cv_id):
        """Deletes a CV entry from SQLite and its content from ChromaDB."""
        try:
            # Get paths before deleting from SQLite to delete files
            cv_info = self.get_cv(cv_id=cv_id)
            if not cv_info:
                logger.warning(f"CV with ID {cv_id} not found for deletion.")
                return False

            self.cursor.execute('DELETE FROM cv_data WHERE id = ?', (cv_id,))
            self.conn.commit()
            logger.info(f"CV with ID {cv_id} deleted from SQLite.")

            if self.cv_collection:
                self.cv_collection.delete(ids=[str(cv_id)])
                logger.info(f"CV content deleted from ChromaDB for ID: {cv_id}")
            
            # Optionally delete the actual files
            if os.path.exists(cv_info['original_docx_path']):
                os.remove(cv_info['original_docx_path'])
                logger.info(f"Deleted original DOCX file: {cv_info['original_docx_path']}")
            if os.path.exists(cv_info['markdown_path']):
                os.remove(cv_info['markdown_path'])
                logger.info(f"Deleted Markdown file: {cv_info['markdown_path']}")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting CV with ID {cv_id}: {e}")
            return False

    def search_cvs(self, query_text, n_results=5):
        """
        Performs a similarity search in ChromaDB and retrieves matching CVs from SQLite.
        """
        if not self.cv_collection:
            logger.error("ChromaDB collection not initialized. Cannot perform search.")
            return []

        try:
            # Query ChromaDB
            results = self.cv_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=['metadatas', 'documents', 'distances']
            )
            
            if not results or not results['ids'] or not results['ids'][0]:
                logger.info("No relevant CVs found in ChromaDB.")
                return []

            found_cv_ids = [int(cv_id) for cv_id in results['ids'][0]]
            
            # Retrieve full CV data from SQLite
            cvs_data = []
            for i, cv_id in enumerate(found_cv_ids):
                cv_info = self.get_cv(cv_id=cv_id)
                if cv_info:
                    cv_info['chroma_distance'] = results['distances'][0][i]
                    cvs_data.append(cv_info)
            
            # Sort by distance (lower distance means higher relevance)
            cvs_data.sort(key=lambda x: x['chroma_distance'])
            
            logger.info(f"Found {len(cvs_data)} relevant CVs for query.")
            return cvs_data
        except Exception as e:
            logger.error(f"Error searching CVs: {e}")
            return []

    def close(self):
        """Closes the SQLite database connection."""
        self.conn.close()
        logger.info("SQLite database connection closed.")

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    db = CVDatabase()

    # Add a dummy CV
    # cv_id = db.add_cv(
    #     original_docx_path="/home/steeve/cv_format/inputs/dummy_cv.docx",
    #     markdown_path="/home/steeve/cv_format/outputs/dummy_cv.md",
    #     extracted_text="This is a dummy CV content about a software engineer with Python and Flask skills.",
    #     availability_date="2025-07-01",
    #     collaborator_wishes="Remote work, AI projects"
    # )
    # if cv_id:
    #     print(f"Added CV with ID: {cv_id}")

    # # Get CV by ID
    # retrieved_cv = db.get_cv(cv_id=cv_id)
    # if retrieved_cv:
    #     print(f"Retrieved CV: {retrieved_cv}")

    # # Update CV
    # if cv_id:
    #     db.update_cv(cv_id, availability_date="2025-08-01", extracted_text="Updated dummy CV content with more details on AI.")
    #     updated_cv = db.get_cv(cv_id=cv_id)
    #     print(f"Updated CV: {updated_cv}")

    # # Search CVs
    # search_results = db.search_cvs("Looking for a software engineer with AI experience")
    # print("\nSearch Results:")
    # for result in search_results:
    #     print(f"  - CV ID: {result['id']}, Path: {result['original_docx_path']}, Distance: {result['chroma_distance']}")

    # # Delete CV
    # if cv_id:
    #     db.delete_cv(cv_id)
    #     print(f"Deleted CV with ID: {cv_id}")
    #     deleted_cv = db.get_cv(cv_id=cv_id)
    #     print(f"CV after deletion: {deleted_cv}")

    db.close()