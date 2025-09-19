from flask import Flask, send_from_directory, render_template
from flask import request, send_file, jsonify, Blueprint
import os
import logging
import argparse
import json

from utils import allowed_file, UPLOAD_FOLDER, OUTPUT_FOLDER, ensure_directories_exist, process_tool1_upload, process_tool2_upload, get_download_filepath, process_tool3_upload, search_cv_entries, delete_cv_entry, update_cv_entry, db # Import db instance

# Configure logging
logging.getLogger("unstructured").setLevel(logging.ERROR)
logging.getLogger("unstructured.trace").setLevel(logging.CRITICAL)
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Réduire la verbosité des bibliothèques LLM et HTTP
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("google.generativeai").setLevel(logging.WARNING)
logging.getLogger("google.api_core").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING) 
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d - %(funcName)s()]')
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['LLM_MODEL'] = 'gpt-4o'
app.config['LLM_MODEL'] = 'gemini-2.0-flash'

# Créer un blueprint pour les fichiers dev
dev_bp = Blueprint('dev', __name__, static_folder='dev', static_url_path='/dev')

# Enregistrer le blueprint
app.register_blueprint(dev_bp)

def load_models_from_json():
    """Loads all active template models from modeles.json."""
    try:
        models_path = os.path.join(os.path.dirname(__file__), '..', 'ressources', 'modeles.json')
        with open(models_path, 'r', encoding='utf-8') as f:
            models = json.load(f)
        # Filter for models with status "ON"
        active_models = [model for model in models if model.get('status') == 'ON']
        return active_models
    except Exception as e:
        logger.error(f"Could not load or parse modeles.json: {e}")
        return []

def load_template_config(app_instance):
    """Loads default template configuration from modeles.json into app.config."""
    # Use the helper to get all active models
    models = load_models_from_json()
    if models:
        # Using the first active template as default
        default_template = models[0]
        app_instance.config['DEFAULT_TEMPLATE_NAME'] = default_template.get('name', 'Default')
        app_instance.config['DEFAULT_TEMPLATE_PATH'] = default_template.get('path')
        logger.info(f"Default template loaded: {app_instance.config['DEFAULT_TEMPLATE_NAME']} from {app_instance.config['DEFAULT_TEMPLATE_PATH']}")
    else:
        logger.error("No active models found in modeles.json or file could not be loaded.")
        app_instance.config['DEFAULT_TEMPLATE_NAME'] = "Error"
        app_instance.config['DEFAULT_TEMPLATE_PATH'] = None

load_template_config(app)
ensure_directories_exist()

# Route for the main page
@app.route('/')
def index():
    logger.info("Rendering the main page")
    # The template name is now loaded into app.config at startup
    template_name = app.config.get('DEFAULT_TEMPLATE_NAME', 'Default')
    return render_template('frontpage.html', template_name=template_name)

@app.route('/dev/auth/login', methods=['POST'])
def login():
    logger.info("Authentification")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/auth/logout', methods=['POST'])
def logout():
    logger.info("Déconnexion")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/auth/check', methods=['GET'])
def check_auth():
    logger.info("Check authentification")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# PAGES PRINCIPALES (RENDU HTML)
# =============================================================================

@app.route('/dev/', methods=['GET'])
def home():
    logger.info("Accès à la page d'accueil")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/administration', methods=['GET'])
def administration():
    logger.info("Accès à la page d'administration")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/collaborateurs/creer', methods=['GET'])
def create_collaborator_page():
    logger.info("Accès à la page de création d'un collaborateurs")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/collaborateurs/liste', methods=['GET'])
def list_collaborators_page():
    logger.info("Accès à la page des collaborateurs")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/collaborateurs/<int:collaborator_id>', methods=['GET'])
def collaborator_profile_page(collaborator_id):
    logger.info("Accès à la page d'un collaborateurs")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/missions/creer', methods=['GET'])
def create_mission_page():
    logger.info("Accès à la page de création d'une missions")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/missions/liste', methods=['GET'])
def list_missions_page():
    logger.info("Accès à la page des collaborateurs")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/missions/<int:mission_id>', methods=['GET'])
def mission_profile_page(mission_id):
    logger.info("Accès à la fiche des missions")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/clients/liste', methods=['GET'])
def list_clients_page():
    logger.info("Accès à la liste des clients")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/clients/<int:client_id>', methods=['GET'])
def client_profile_page(client_id):
    logger.info("Accès à la fiche client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/missions/en-cours', methods=['GET'])
def current_missions_page():
    logger.info("Accès à la page des des missions en cours")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/recherche', methods=['GET'])
def search_page():
    logger.info("Accès à la page de recherche globale")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API GESTION DES COLLABORATEURS
# =============================================================================

@app.route('/dev/api/collaborateurs', methods=['GET'])
def get_collaborators():
    logger.info("Accès à la liste des collaborateurs")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs', methods=['POST'])
def create_collaborator():
    logger.info("Création d'un collaborateur collaborateurs")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>', methods=['GET'])
def get_collaborator(collaborator_id):
    logger.info("Accès à la fiche d'un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>', methods=['PUT'])
def update_collaborator(collaborator_id):
    logger.info("Modification d'un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>', methods=['DELETE'])
def delete_collaborator(collaborator_id):
    logger.info("Suppression d'un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>/cv', methods=['PUT'])
def update_collaborator_cv(collaborator_id):
    logger.info("Modification d'un cv pour un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>/cv/regenerate', methods=['POST'])
def regenerate_cv_section(collaborator_id):
    logger.info("Ajout d'un nouveau cv pour un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>/experiences', methods=['POST'])
def add_experience(collaborator_id):
    logger.info("Ajout d'une nouvelle expérience pour le cv d'un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>/cv/optimize', methods=['POST'])
def optimize_cv(collaborator_id):
    logger.info("Optimisation du cv du collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>/cv/download', methods=['GET'])
def download_cv_uti(collaborator_id):
    logger.info("Téléchargement du cv d'un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>/cv/send-email', methods=['POST'])
def send_cv_email(collaborator_id):
    logger.info("Envoi du cv du collaborateur par email")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>/missions/assign', methods=['POST'])
def assign_mission_to_collaborator(collaborator_id):
    logger.info("Assignation d'une mission à un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/<int:collaborator_id>/missions/unassign', methods=['POST'])
def unassign_mission_from_collaborator(collaborator_id):
    logger.info("Désassignation d'une mission à un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/import-cv', methods=['POST'])
def import_cv():
    logger.info("Création d'un collaborateur à partir d'un cv")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/collaborateurs/search', methods=['POST'])
def search_collaborators():
    logger.info("Accès à la page de recherche des collaborateurs")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API GESTION DES MISSIONS
# =============================================================================

@app.route('/dev/api/missions', methods=['GET'])
def get_missions():
    logger.info("Accès à la page des missions")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions', methods=['POST'])
def create_mission():
    logger.info("Création d'une mission")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>', methods=['GET'])
def get_mission(mission_id):
    logger.info("Accès à la fiche d'une mission")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>', methods=['PUT'])
def update_mission(mission_id):
    logger.info("Modification d'une mission")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>', methods=['DELETE'])
def delete_mission(mission_id):
    logger.info("Suppression d'une mission")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>/collaborateurs/search', methods=['POST'])
def search_collaborators_for_mission(mission_id):
    logger.info("Recherche de collaborateur pour une mission")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>/collaborateurs/assign', methods=['POST'])
def assign_collaborator_to_mission(mission_id):
    logger.info("Assignation d'une mission à un collaborateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>/contact/assign', methods=['POST'])
def assign_contact_to_mission(mission_id):
    logger.info("Assignation d'un contact")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/en-cours', methods=['GET'])
def get_current_missions():
    logger.info("Accès à la page des missions en cours")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>/rapports', methods=['GET'])
def get_mission_reports(mission_id):
    logger.info("Récupération des rapports d'une mission")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>/rapports', methods=['POST'])
def add_mission_report(mission_id):
    logger.info("Ajout d'un rapport de mission")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/missions/<int:mission_id>/rapports/<int:report_id>/download', methods=['GET'])
def download_mission_report(mission_id, report_id):
    logger.info("Téléchargement d'un rapport de mission")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API GESTION DES CLIENTS
# =============================================================================

@app.route('/dev/api/clients', methods=['GET'])
def get_clients():
    logger.info("Accès à la page des clients")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients', methods=['POST'])
def create_client():
    logger.info("Création d'un client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    logger.info("Accès à la fiche d'un client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    logger.info("Modification d'un client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    logger.info("Suppression d'un client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients/<int:client_id>/contacts', methods=['GET'])
def get_client_contacts(client_id):
    logger.info("Récupération des contacts d'un client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients/<int:client_id>/contacts', methods=['POST'])
def create_client_contact(client_id):
    logger.info("Ajout d'un contact d'un client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients/<int:client_id>/contacts/<int:contact_id>', methods=['PUT'])
def update_client_contact(client_id, contact_id):
    logger.info("Modifications d'un contact d'un client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients/<int:client_id>/contacts/<int:contact_id>', methods=['DELETE'])
def delete_client_contact(client_id, contact_id):
    logger.info("Suppression d'un contact d'un client")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/clients/<int:client_id>/commercial', methods=['PUT'])
def assign_commercial_to_client(client_id):
    logger.info("Modification du commercial d'un client")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API GESTION DES COMMERCIAUX (ADMIN SEULEMENT)
# =============================================================================

@app.route('/dev/api/commerciaux', methods=['GET'])
def get_commercials():
    logger.info("Accès à la listes des commerciaux")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/commerciaux', methods=['POST'])
def create_commercial():
    logger.info("Création d'un commercial")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/commerciaux/<int:commercial_id>', methods=['GET'])
def get_commercial(commercial_id):
    logger.info("Accès à la fiche d'un commercial")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/commerciaux/<int:commercial_id>', methods=['PUT'])
def update_commercial(commercial_id):
    logger.info("Modification d'un commercial")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/commerciaux/<int:commercial_id>', methods=['DELETE'])
def delete_commercial(commercial_id):
    logger.info("Suppression d'un commercial")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API INTELLIGENCE ARTIFICIELLE
# =============================================================================

@app.route('/dev/api/ia/analyze-cv', methods=['POST'])
def analyze_cv_with_ai():
    logger.info("Analyse du cv par l'ia")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/ia/analyze-mission', methods=['POST'])
def analyze_mission_with_ai():
    logger.info("Analyse de la mission par l'ia")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/ia/match-collaborateur-mission', methods=['POST'])
def match_collaborator_mission_ai():
    logger.info("Recherche des collaborateurs pour une mission par l'ia")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/ia/optimize-cv-for-mission', methods=['POST'])
def optimize_cv_for_mission_ai():
    logger.info("Optimisation d'un cv pour une mission par l'ia")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/ia/regenerate-section', methods=['POST'])
def regenerate_section_ai():
    logger.info("Regénérer une section d'un cv par l'ia")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API RECHERCHE GLOBALE
# =============================================================================

@app.route('/dev/api/recherche/keyword', methods=['POST'])
def global_search():
    logger.info("Execution d'une recherche")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API GESTION DES FICHIERS
# =============================================================================

@app.route('/dev/api/files/upload', methods=['POST'])
def upload_file():
    logger.info("Envoi d'un fichier")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    logger.info("Téléchargement d'un fichier")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    logger.info("Suppression d'un fichier")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API GÉNÉRATION DE CV
# =============================================================================

@app.route('/dev/api/cv/generate-uti/<int:collaborator_id>', methods=['POST'])
def generate_cv_uti(collaborator_id):
    logger.info("Génération d'un cv au format UTI")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/cv/generate-optimized/<int:collaborator_id>/<int:mission_id>', methods=['POST'])
def generate_optimized_cv(collaborator_id, mission_id):
    logger.info("Optimisation d'un cv pour une mission")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/cv/send-email/<int:collaborator_id>', methods=['POST'])
def send_cv_by_email(collaborator_id):
    logger.info("Envoyer le cv par email")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/cv/versions/<int:collaborator_id>', methods=['GET'])
def get_cv_versions(collaborator_id):
    logger.info("Récupération de la liste des cvs d'un collaborateur")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# API GESTION DES SESSIONS ET SÉCURITÉ
# =============================================================================

@app.route('/dev/api/profile', methods=['GET'])
def get_user_profile():
    logger.info("Récupération des droits de l'utilisateur")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/api/permissions/<string:action>', methods=['GET'])
def check_permission(action):
    logger.info("Vérification si l'utilisateur a le droit de faire l'eaction")
    return send_from_directory('dev', 'index.html')

# =============================================================================
# ROUTES D'ERREUR ET STATUT
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Gestion des erreurs 404"""
    pass

@app.errorhandler(403)
def forbidden(error):
    """Gestion des erreurs 403 - Accès interdit"""
    pass

@app.errorhandler(500)
def internal_error(error):
    """Gestion des erreurs 500 - Erreur serveur"""
    pass

# =============================================================================
# MIDDLEWARE ET DÉCORATEURS DE SÉCURITÉ
# =============================================================================

def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    def decorated_function(*args, **kwargs):
        # Vérifier le token d'authentification
        return f(*args, **kwargs)
    return decorated_function

def require_role(role):
    """Décorateur pour vérifier le rôle utilisateur"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # Vérifier le rôle de l'utilisateur
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin(f):
    """Décorateur pour les routes admin seulement"""
    return require_role('admin')(f)

def require_commercial_or_admin(f):
    """Décorateur pour les routes commercial ou admin"""
    def decorated_function(*args, **kwargs):
        # Vérifier si l'utilisateur est commercial ou admin
        return f(*args, **kwargs)
    return decorated_function

"""
@app.route('/dev/<path:path>')
def dev_files(path):
    #Serve all files from dev directory with correct MIME types
    logger.info(f"Serving dev file: {path}")
    return send_from_directory('dev', path)

# Example route for handling file uploads (Tool 1)
@app.route('/upload/tool1', methods=['POST'])
def upload_tool1():
    logger.info("New upload request received for Tool 1")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request form data: {dict(request.form)}")
    logger.debug(f"Request files: {list(request.files.keys())}")

    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file in the request")
        return jsonify({'error': 'No selected file'}), 400
    logger.info(f"Processing file: {file.filename} ({file.content_type})")

    if not allowed_file(file.filename):
        logger.error("File type not allowed")
        return jsonify({'error': 'File type not allowed'}), 400

    result, error, status_code = process_tool1_upload(file, app.config)
    if error:
        return jsonify({'error': error}), status_code
    return jsonify(result), status_code

# Example route for handling file uploads (Tool 2)
@app.route('/upload/tool2', methods=['POST'])
def upload_tool2():
    logger.info("New upload request received for Tool 2")
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file in the request")
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        logger.error("File type not allowed")
        return jsonify({'error': 'File type not allowed'}), 400

     # Find the path for the selected template
    template_path = None
    template_name = request.form.get('template_name')
    if template_name:
        models = load_models_from_json()
        for model in models:
            if model.get('name') == template_name:
                template_path = model.get('path')
                break
    
    # If no template is selected or found, fall back to the default
    if not template_path:
        logger.warning(f"Template '{template_name}' not found or not provided. Using default.")
        template_path = app.config.get('DEFAULT_TEMPLATE_PATH')

    if not template_path:
        logger.error("No template path configured (default or selected).")
        return jsonify({'error': 'Server configuration error: No template available.'}), 500

    # Create a temporary config for this request to pass the correct template path
    request_config = app.config.copy()
    request_config['DEFAULT_TEMPLATE_PATH'] = template_path
    
    logger.info(f"Processing file upload with template: {template_path}")
    result, error, status_code = process_tool2_upload(file, request_config)
    if error:
        return jsonify({'error': error}), status_code
    return jsonify(result), status_code

# Example route for downloading a file (you'll need to implement the actual file creation)
@app.route('/download/<filename>')
def download_file(filename):
    logger.info(f"Attempting to download file: {filename}")
    filepath, error, status_code = get_download_filepath(filename, app.config)
    if error:
        return error, status_code
    return send_file(filepath, as_attachment=True, download_name=filename)

# Route for the CV management page
@app.route('/cv_manage')
def cv_manage():
    logger.info("Rendering the CV management page")
    return render_template('cv_management.html')

# API endpoint to list all CVs
@app.route('/api/cv/list', methods=['GET'])
def list_cvs():
    logger.info("Fetching all CVs from the database")
    try:
        all_cvs = db.cursor.execute('SELECT * FROM cv_data').fetchall()
        columns = [description[0] for description in db.cursor.description]
        cvs_as_dict = [dict(zip(columns, row)) for row in all_cvs]
        return jsonify({'cvs': cvs_as_dict}), 200
    except Exception as e:
        logger.error(f"Error listing CVs: {e}")
        return jsonify({'error': f'Failed to retrieve CVs: {str(e)}'}), 500

# API endpoint to list available templates
@app.route('/api/templates', methods=['GET'])
def list_templates():
    logger.info("Fetching all available templates")
    models = load_models_from_json()
    if not models:
        return jsonify({'error': 'No templates available'}), 500
    # Send only necessary info to the frontend
    template_info = [{'name': model.get('name'), 'description': model.get('description')} for model in models]
    return jsonify(template_info), 200

@app.route('/api/template/preview/<template_name>', methods=['GET'])
def get_template_preview(template_name):

    #Return a preview snippet (HTML) of the DOCX template identified by template_name.

    models = load_models_from_json()
    template = next((m for m in models if m.get('name') == template_name), None)
    if not template:
        return jsonify({'error': 'Template not found'}), 404

    template_path = template.get('path')
    if not template_path or not os.path.isfile(template_path):
        return jsonify({'error': 'Template file not found'}), 404

    try:
        doc = Document(template_path)
        # Extract first 3 paragraphs as preview
        preview_paragraphs = doc.paragraphs[:3]
        preview_html = ""
        for para in preview_paragraphs:
            # Escape HTML special chars if needed, here we keep it simple
            preview_html += f"<p>{para.text}</p>"
        return jsonify({'preview_html': preview_html})
    except Exception as e:
        logger.error(f"Error reading DOCX for preview: {e}")
        return jsonify({'error': 'Failed to generate preview'}), 500

# API endpoint for handling file uploads (Tool 3 - Word document capture)
@app.route('/upload/tool3', methods=['POST'])
def upload_tool3():
    logger.info("New upload request received for Tool 3 (Word document capture)")
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file in the request")
        return jsonify({'error': 'No selected file'}), 400
    
    result, error, status_code = process_tool3_upload(file, app.config)
    if error:
        return jsonify({'error': error}), status_code
    return jsonify(result), status_code

# API endpoint for searching CVs
@app.route('/api/cv/search', methods=['GET'])
def search_cv():
    logger.info("New search request received for CVs")
    query_text = request.args.get('query')

    if not query_text:
        logger.error("No query text provided for CV search")
        return jsonify({'error': 'No query text provided'}), 400
    
    results, error, status_code = search_cv_entries(query_text)
    if error:
        return jsonify({'error': error}), status_code
    return jsonify(results), status_code

# API endpoint for deleting a CV
@app.route('/api/cv/delete/<int:cv_id>', methods=['DELETE'])
def delete_cv(cv_id):
    logger.info(f"New delete request received for CV ID: {cv_id}")
    result, error, status_code = delete_cv_entry(cv_id)
    if error:
        return jsonify({'error': error}), status_code
    return jsonify(result), status_code

# API endpoint for updating CV metadata
@app.route('/api/cv/update/<int:cv_id>', methods=['PUT'])
def update_cv(cv_id):
    logger.info(f"New update request received for CV ID: {cv_id}")
    data = request.get_json()
    availability_date = data.get('availability_date')
    collaborator_wishes = data.get('collaborator_wishes')

    if not availability_date and not collaborator_wishes:
        logger.error("No update data provided for CV")
        return jsonify({'error': 'No update data provided (availability_date or collaborator_wishes)'}), 400
    
    result, error, status_code = update_cv_entry(cv_id, availability_date, collaborator_wishes)
    if error:
        return jsonify({'error': error}), status_code
    return jsonify(result), status_code
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Flask app.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the Flask app on.')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=True)