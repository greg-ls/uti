# /// script
# dependencies = [
#   "python-docx",
#   "llama_parser",
#   "pdfplumber",
#   "bs4",
#   "setuptools", # Required by llama_index (a dependency of llama_parser)
# ]
# ///
# To run this script, use the following command:
# uv pdf_content.py

from docx import Document
import os
import llama_parser  # Import our llama_parser module
import pdfplumber
from collections import Counter
from bs4 import BeautifulSoup
import subprocess
from .document_loader_LLM import document_loader

def detect_repeating_headers_footers(pdf_path, threshold=0.5):
    """
    Détecte les en-têtes et pieds de page récurrents dans un PDF.
    Supprime ces éléments s'ils apparaissent dans plus de "threshold" % des pages.
    """
    headers = []
    footers = []
    all_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                if len(lines) > 2:  # Vérifier qu'il y a assez de lignes
                    headers.append(lines[0])  # Première ligne (en-tête potentiel)
                    footers.append(lines[-1])  # Dernière ligne (pied de page potentiel)
                all_text.append(lines)

    # Détecter les éléments répétitifs
    header_counts = Counter(headers)
    footer_counts = Counter(footers)

    # Filtrer ceux qui apparaissent fréquemment (ex: > 50% des pages)
    total_pages = len(all_text)
    common_headers = {h for h, c in header_counts.items() if c / total_pages > threshold}
    common_footers = {f for f, c in footer_counts.items() if c / total_pages > threshold}

    # Supprimer ces en-têtes et pieds de page détectés
    cleaned_text = []
    for lines in all_text:
        filtered_lines = [line for line in lines if line not in common_headers and line not in common_footers]
        cleaned_text.append("\n".join(filtered_lines))

    return "\n".join(cleaned_text)

def extract_text_from_docx_combined(docx_path):
    """
    Extracts text from a DOCX file using both python-docx and llama_parser,
    then combines and deduplicates the results.
    """
    # Extract with python-docx
    docx_text_python = extract_text_from_docx(docx_path)

    # Extract with llama_parser
    try:
        docx_text_llama = llama_parser.extract_text_from_docx(docx_path)
    except Exception as e:
        print(f"Error extracting text with llama_parser: {str(e)}")
        docx_text_llama = ""  # Fallback to empty string if llama_parser fails

    # Combine and deduplicate (basic deduplication for demonstration)
    combined_text = docx_text_python + "\n"
    if docx_text_llama:
        for line in docx_text_llama.splitlines():
            if line.strip() and line not in combined_text: # Avoid adding empty lines and ensure uniqueness
                combined_text += line + "\n"

    return combined_text

def extract_text_from_pdf_combined(pdf_path):
    """
    Extracts text from a PDF file using both PyPDF2 and llama_parser,
    then combines and deduplicates the results.
    """
    # Extract with PyPDF2
    pdf_text_plumber = extract_text_from_pdf(pdf_path) # Using pdfplumber via extract_text_from_pdf

    # Extract with llama_parser
    try:
        pdf_text_llama = llama_parser.extract_text_from_pdf(pdf_path)
    except Exception as e:
        print(f"Error extracting text with llama_parser: {str(e)}")
        pdf_text_llama = ""  # Fallback to empty string if llama_parser fails

    # Combine and deduplicate
    combined_text = pdf_text_plumber + "\n"
    if pdf_text_llama:
        for line in pdf_text_llama.splitlines():
            if line.strip() and line not in combined_text: # Avoid adding empty lines and ensure uniqueness
                combined_text += line + "\n"

    return combined_text

def extract_text_from_docx(docx_path):
    """Extracts the full text of a DOCX file, including headers, footers, and tables."""
    doc = Document(docx_path)
    full_text = []

    # Extract headers
    for section in doc.sections:
        # Headers
        header = section.header
        if header:
            for paragraph in header.paragraphs:
                full_text.append(paragraph.text)
            for table in header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        full_text.append(cell.text)

        # Footers
        footer = section.footer
        if footer:
            for paragraph in footer.paragraphs:
                full_text.append(paragraph.text)
            for table in footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        full_text.append(cell.text)

    # Extract body
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)

    # Extract tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                full_text.append(cell.text)

    return '\n'.join(line for line in full_text if line.strip())

def extract_text_from_pdf(pdf_path):
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text.append(page.extract_text())

    return '\n'.join(filter(None, full_text))

def extract_text_from_html(html_path):
    """Extracts the full text of an HTML file."""
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser') # Consider 'lxml' for performance if installed
    full_text = soup.get_text(separator='\n')

    return '\n'.join(line for line in full_text.splitlines() if line.strip()) # Clean up empty lines

def extract_text_to_file_combined(input_path, output_path=None, config=None):
    """
    Extracts text from a DOCX, PDF, or HTML file using combined extraction methods and saves it to a text file.

    Args:
        input_path (str): Path to the input file (DOCX, PDF, or HTML)
        output_path (str, optional): Path to the output file. If not specified,
                                   uses the same name as the input file with a .txt extension.
    """
    # Check file extension
    file_ext = os.path.splitext(input_path)[1].lower()
    # If output_path is not specified, create output in ../output directory
    if not output_path:
        os.makedirs('/home/steeve/cv_format/outputs', exist_ok=True)
        base_name = os.path.basename(os.path.splitext(input_path)[0])
        # output_path = os.path.join('/home/steeve/cv_format/outputs', f'{base_name}.txt')
        # output_path = os.path.abspath(output_path)
        output_path = f'/home/steeve/cv_format/outputs/{base_name}.txt'

    try:
        model_name = config.get('LLM_MODEL') if config else None
        # document_loader(input_path, output_path, model=model_name)
        document_loader(input_path, output_path, model=None)
    except Exception as e:
        print(f"Error during text extraction: {str(e)}")
        raise

    if not os.path.exists(output_path):
        raise Exception(f"Output file not created: {output_path}")

if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        extract_text_to_file_combined(input_file, output_file)
    else:
        print("Usage: python pdf_content.py input_file [output_file]")

def extract_raw_pdf(pdf_file_path, txt_file_path=None, config=None):
    """
    Extracts text from a PDF file using the pdftotext command,
    processes the text using Gemini, and saves the result to the output file.

    Args:
        pdf_file_path (str): Path to the input PDF file.
        txt_file_path (str): Path to the output text file.

    Returns:
        bool: True if the command executes successfully, False otherwise.
    """
    if txt_file_path is None: txt_file_path = pdf_file_path.replace('.pdf', '.txt')

    # The command was referencing 'config' which was not passed in.
    # It also used 'input_file' and 'output_file' which are not defined in this scope.
    # This is corrected to use function arguments and the passed-in config.
    model = "gemini-2.0-flash"  # Default model
    if config and 'LLM_MODEL' in config:
        model = config['LLM_MODEL']
    print(f"Using model: {model}, processing file: {pdf_file_path} in extract_raw_pdf")


    command = f'pdftotext -layout "{pdf_file_path}" "{txt_file_path}"'
    command = f'python3 document_loader_LLM.py --model gemini-2.0-flash -v " {input_file}" "{output_file}"'
    command = f'python3 document_loader_LLM.py --model {model} -v " {input_file}" "{output_file}"'
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing pdftotext: {e}")
        return False
    except FileNotFoundError:
        print("Error: pdftotext command not found. Please ensure it is installed and in your system's PATH.")
        return False
    except Exception as e:
        print(f"Error during text processing: {e}")
        return False

if __name__ == "__main__":
    scr_file = r"/home/steeve/cv_format/inputs/ESSAME Otto.pdf"
    tgt_file = r"/home/steeve/cv_format/outputs/ESSAME Otto.txt"
    if extract_raw_pdf(scr_file, tgt_file):
        print("Raw PDF extracted successfully.")
    else:
        print("Failed to extract raw PDF.")
