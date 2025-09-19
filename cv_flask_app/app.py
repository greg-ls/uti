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

@app.route('/dev')
def dev():
    logger.info("Development route accessed")
    return send_from_directory('dev', 'index.html')

@app.route('/dev/<path:path>')
def dev_files(path):
    """Serve all files from dev directory with correct MIME types"""
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
    """
    Return a preview snippet (HTML) of the DOCX template identified by template_name.
    """
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Flask app.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the Flask app on.')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=True)