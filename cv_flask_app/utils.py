import os
import logging
import re
import inspect

from features.content_to_json import content_to_json
from features.word_interact import generate_word_new, generate_word
from features.extract_content import extract_text_to_file_combined
from features.cv_database import CVDatabase
from features.docx_to_markdown import convert_docx_to_markdown # Will create this file
from features.llm_agent import LLMAgent

# Configure logging
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = '/home/steeve/cv_format/inputs'  # Relative path to target directory
OUTPUT_FOLDER = '/home/steeve/cv_format/outputs'  # Relative path to output directory
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'} # Added 'md'
db = CVDatabase() # Initialize the database

def ensure_directories_exist():
    # Ensure the upload and output folders exist with proper permissions
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        logger.info(f"Ensured upload directory exists at: {UPLOAD_FOLDER}")
        logger.info(f"Ensured output directory exists at: {OUTPUT_FOLDER}")
        # Verify write permissions
        if not os.access(UPLOAD_FOLDER, os.W_OK):
            raise RuntimeError(f"Write permission denied for directory: {UPLOAD_FOLDER}")
        if not os.access(OUTPUT_FOLDER, os.W_OK):
            raise RuntimeError(f"Write permission denied for directory: {OUTPUT_FOLDER}")
    except Exception as e:
        logger.error(f"Fatal directory error: {str(e)}")
        raise

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_tool1_upload(file, app_config):
    logger = logging.getLogger(__name__)
    filename = file.filename
    if not filename:
        logger.error("Invalid file name")
        return None, 'Invalid file name', 400

    filepath = os.path.join(app_config['UPLOAD_FOLDER'], filename)
    logger.info(f"Attempting to save upload to: {filepath}")

    try:
        # Verify directory permissions again before write
        if not os.access(os.path.dirname(filepath), os.W_OK):
            raise IOError("Destination directory not writable")

        file.save(filepath)
        logger.info(f"File successfully saved to: {filepath}")
        logger.info(f"Absolute path verification: {os.path.abspath(filepath)}")

        # Conversion call
        converted_filename = filename.replace('.docx', '.txt').replace('.pdf', '.txt') #f"converted_{filename}.txt"
        converted_filepath = os.path.join(app_config['OUTPUT_FOLDER'], converted_filename)
        try:
            extract_text_to_file_combined(filepath, converted_filepath, config=app_config)
        except Exception as e:
            logger.error(f"Error in extract_text_to_file_combined: {str(e)}, stdout: {getattr(e, 'stdout', None)}, stderr: {getattr(e, 'stderr', None)}")
            return None, f'File conversion failed: {str(e)}', 500

        # deal with columns
        with open(converted_filepath, 'r') as f_read:
            # Read the content of the file
            content = f_read.read()
        # Process
        # agt = LLMAgent("gpt-4o")
        agt = LLMAgent(app_config['LLM_MODEL'])
        sys = """Tu es un expert dans la mise en forme de fichiers texte. Ton objectif est de fournir une restitution intégrale et fidèle du texte tout en respectant des règles spécifiques de traitement des colonnes et de présentation. 
        Tu dois restituer le texte de manière structurée et lisible.

**Objectifs :**
* Gérer spécifiquement les données réparties en colonnes pour une lisibilité optimale.
* Maintenir la liaison entre les données de colonnes différentes lorsqu'elles sont intrinsèquement liées.
* Réorganiser le contenu si nécessaire pour une présentation logique et cohérente (par exemple, regrouper les informations d'une section avant de passer à une autre, même si elles étaient visuellement séparées en colonnes).

**Comportements et Règles :**
1.  **Gestion des Colonnes Liées :**
    * Si deux colonnes contiennent des informations directement liées et formant une entité cohérente (ex: année et diplôme), conserve leur agencement tel quel. Par exemple, '2000 Bac scientifique série E' doit rester une ligne unique.
    * Le but est de ne pas 'séparer' artificiellement des informations qui sont naturellement groupées.
2.  **Réorganisation du Contenu :**
    * Si des sections de texte sont disposées en colonnes mais représentent des thèmes distincts (ex: 'PROFIL PERSONNEL' dans une colonne et 'EXPÉRIENCES PROFESSIONNELLES' dans une autre, avec leurs contenus respectifs dispersés), réorganise le contenu pour présenter chaque section intégralement avant de passer à la suivante.
    * La présentation finale doit être linéaire et logique, comme si le texte avait été écrit d'un seul bloc, de haut en bas, pour chaque section.
    * Par exemple, pour le contenu fourni en exemple : d'abord le 'PROFIL PERSONNEL' complet, puis les 'EXPÉRIENCES PROFESSIONNELLES' complètes, même si dans le PDF original, elles étaient côte à côte.
3.  **Format de Sortie :** Restitue le texte extrait sous forme de chaîne de caractères non formatée, en respectant les retours à la ligne et les espacements pour maintenir la lisibilité, et sans indiquer les sources.
4.  **Précision et Intégrité :** Assure-toi que l'intégralité du texte  (corps du document) est capturée sans omissions ni ajouts.

**Ton ton et ta personnalité :**
* Professionnel et rigoureux.
* Axé sur la précision et la fidélité de l'extraction.
* Clair et concis dans tes réponses.

N'ajoute ni commentaire ni explication.
Restitue bien le contenu intégral du document, sans indiquer les sources."""
        sys = """Tu es un expert dans la mise en forme de contenu au format texte. T
ton objectif est de fournir une restitution intégrale et fidèle du texte contenu dans le corps d'un PDF, tout en respectant des règles spécifiques de traitement des colonnes et de présentation. Tout le contenu initial doit se retrouver dans le contenu mis en forme.
**Objectifs :**
    * Gérer spécifiquement les données réparties en colonnes pour une lisibilité optimale.
    * Maintenir la liaison entre les données de colonnes différentes lorsqu'elles sont intrinsèquement liées.
    * Réorganiser le contenu si nécessaire pour une présentation logique et cohérente (par exemple, regrouper les informations d'une section avant de passer à une autre, même si elles étaient visuellement séparées en colonnes).
**Comportements et Règles :**
    1.  **Gestion des Colonnes Liées :**
        * Si deux colonnes contiennent des informations directement liées et formant une entité cohérente (ex: année et diplôme), conserve leur agencement tel quel. Par exemple, '2000 Bac scientifique série E' doit rester une ligne unique.     
        * Le but est de ne pas 'séparer' artificiellement des informations qui sont naturellement groupées.  
    2.  **Réorganisation du Contenu :**
        * Si des sections de texte sont disposées en colonnes mais représentent des thèmes distincts (ex: 'PROFIL PERSONNEL' dans une colonne et 'EXPÉRIENCES PROFESSIONNELLES' dans une autre, avec leurs contenus respectifs dispersés), réorganise le contenu pour présenter chaque section intégralement avant de passer à la suivante.
        * La présentation finale doit être linéaire et logique, comme si le texte avait été écrit d'un seul bloc, de haut en bas, pour chaque section.
        * Pour le contenu donnée en exemple: d'abord le 'PROFIL PERSONNEL' complet, puis les 'EXPÉRIENCES PROFESSIONNELLES' complètes, même si dans le texte original, elles étaient côte à côte.  
    3.  **Format de Sortie :** 
    Restitue le texte extrait sous forme de chaîne de caractères, en respectant les retours à la ligne et les espacements pour maintenir la lisibilité, et sans indiquer de liens ni de sources.  
    4.  **Précision et Intégrité :** 
    Assure-toi que l'intégralité du texte (corps du document) est capturée sans résumer, omettre ou ajouter des données.  
**Ton ton et ta personnalité :** 
    * Professionnel et rigoureux. 
    * Axé sur la précision et la fidélité de l'extraction. 
    * Clair et concis dans tes réponses.  
    * N'ajoute ni commentaire ni explication. 
"""
        processed_content = agt.get_response_without_history(content, sys)
        # Save the processed content back to the file
        with open(converted_filepath, 'w') as f_write:
            try:
                if isinstance(processed_content, dict) and "text" in processed_content:
                    f_write.write(processed_content["text"])
                else:
                    f_write.write(processed_content)
            except Exception as e:
                f_write.write(f"Erreur lors du rendu du contenu du PDF: {e}")
                f_write.write(processed_content)
                print(f"Erreur lors du rendu du contenu du PDF: {e}")
        return {
            'message': 'File uploaded and converted successfully',
            'filename': converted_filename,
            'path': converted_filepath,
            'absolute_path': os.path.abspath(converted_filepath)
        }, None, 200
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return None, f'File save failed: {str(e)}', 500

def process_tool2_upload(file, app_config):
    logger = logging.getLogger(__name__)
    filename = file.filename
    if not filename:
        logger.error("Invalid file name")
        return None, 'Invalid file name', 400

    filepath = os.path.join(app_config['UPLOAD_FOLDER'], filename)
    logger.info(f"Attempting to save upload to: {filepath}")

    try:
        # Verify directory permissions again before write
        if not os.access(os.path.dirname(filepath), os.W_OK):
            raise IOError("Destination directory not writable")

        file.save(filepath)
        logger.info(f"File successfully saved to: {filepath}")
        logger.info(f"Absolute path verification: {os.path.abspath(filepath)}")

        if filename.endswith('docx'):
            tgt_file = f"extracted_{filename.replace('.docx', '.txt')}"
            extract_text_to_file_combined(filename, tgt_file)
            logger.info(f"Data extraction successful to: {tgt_file}")
            filename = tgt_file
            filepath = os.path.join(app_config['UPLOAD_FOLDER'], filename)
        else:
            ...

        # Conversion call
        base_name = os.path.splitext(filename)[0]
        converted_filename = f"converted_{base_name}.docx"
        converted_filepath = os.path.join(app_config['OUTPUT_FOLDER'], converted_filename)

        # Generate JSON intermediate file
        json_file = f"converted_{base_name}.json"
        json_path = os.path.join(app_config['OUTPUT_FOLDER'], json_file)
        logger.info(f"Generating JSON at: {json_path}")
        try:
            if filename.endswith('.txt'):
                content_to_json(filepath, json_path, prompts_file="/home/steeve/cv_format/ressources/prompts.json")
            else:
                content_to_json(filepath, json_path)
            if not os.path.exists(json_path):
                raise FileNotFoundError(f"JSON file not created at {json_path}")
        except Exception as e:
            logger.error(f"JSON generation failed: {str(e)}")
            return None, f'Content conversion failed: {str(e)}', 500

        # Generate Word document from template
        template_path = app_config.get('DEFAULT_TEMPLATE_PATH')
        if not template_path:
            logger.error("Default template path is not configured.")
            return None, 'Server configuration error: template path missing.', 500
        
        logger.info(f"Using template at: {template_path}")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file missing at {template_path}")

        logger.info(f"Generating Word document at: {converted_filepath}")
        try:
            logger.info(f'{json_path}, {template_path}, {converted_filepath}')
            output_docx = generate_word_new(json_path, template_path, converted_filepath)
            if not os.path.exists(output_docx):
                raise FileNotFoundError(f"Word document not created at {converted_filepath}")
        except Exception as e:
            logger.error(f"Word generation failed: {str(e)}")
            return None, f'Document creation failed: {str(e)}', 500

        return {'message': 'File uploaded and converted successfully',
                      'filename': converted_filename,
                      'path': converted_filepath,
                      'absolute_path': os.path.abspath(converted_filepath)}, None, 200
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return None, f'File processing failed: {str(e)}', 500

def get_download_filepath(filename, app_config):
    logger = logging.getLogger(__name__)
    filepath = os.path.join(app_config['OUTPUT_FOLDER'], filename)
    if os.path.exists(filepath):
        logger.info(f"File found at: {filepath}")
        return filepath, None, None
    else:
        logger.error(f"File not found: {filepath}")
        return None, "File not found", 404

def process_tool3_upload(file, app_config):
    """
    Handles Word document uploads for the new tool (Tool 3).
    Extracts text, converts to Markdown, and stores in the CV database.
    """
    logger = logging.getLogger(__name__)
    filename = file.filename
    if not filename:
        logger.error("Invalid file name")
        return None, 'Invalid file name', 400

    if not filename.lower().endswith('.docx'):
        logger.error("Only DOCX files are allowed for Tool 3 upload.")
        return None, 'Only DOCX files are allowed for this tool', 400

    original_docx_path = os.path.join(app_config['UPLOAD_FOLDER'], filename)
    markdown_filename = os.path.splitext(filename)[0] + '.md'
    markdown_path = os.path.join(app_config['OUTPUT_FOLDER'], markdown_filename)

    try:
        file.save(original_docx_path)
        logger.info(f"Original DOCX file saved to: {original_docx_path}")

        # Extract text and convert to Markdown
        extracted_text = convert_docx_to_markdown(original_docx_path, markdown_path)
        if not extracted_text:
            raise Exception("Failed to extract text or convert DOCX to Markdown.")
        
        # Add to database
        cv_id = db.add_cv(original_docx_path, markdown_path, extracted_text)
        if cv_id is None:
            return None, 'Failed to add CV to database (possibly duplicate)', 500

        return {
            'message': 'CV uploaded, processed, and added to database successfully',
            'cv_id': cv_id,
            'original_docx_path': original_docx_path,
            'markdown_path': markdown_path
        }, None, 200
    except Exception as e:
        logger.error(f"Tool 3 upload failed: {str(e)}")
        return None, f'Processing failed: {str(e)}', 500

def search_cv_entries(query_text):
    """Searches for relevant CVs in the database."""
    logger.info(f"Searching CVs for query: {query_text}")
    results = db.search_cvs(query_text)
    return results, None, 200

def delete_cv_entry(cv_id):
    """Deletes a CV entry from the database."""
    logger.info(f"Deleting CV with ID: {cv_id}")
    success = db.delete_cv(cv_id)
    if success:
        return {'message': f'CV with ID {cv_id} deleted successfully'}, None, 200
    else:
        return None, f'Failed to delete CV with ID {cv_id}', 500

def update_cv_entry(cv_id, availability_date=None, collaborator_wishes=None):
    """Updates metadata for a CV entry in the database."""
    logger.info(f"Updating CV with ID: {cv_id}")
    success = db.update_cv(cv_id, availability_date=availability_date, collaborator_wishes=collaborator_wishes)
    if success:
        return {'message': f'CV with ID {cv_id} updated successfully'}, None, 200
    else:
        return None, f'Failed to update CV with ID {cv_id}', 500