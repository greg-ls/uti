from .llm_agent import LLMAgent
import argparse
import chardet
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d - %(funcName)s()]')
logger = logging.getLogger(__name__)

def content_to_json(scr_file, tgt_file="", model="gemini-2.0-flash", prompts_file="/home/steeve/cv_format/ressources/prompts.json"):
    agent = LLMAgent(model=model, prompts_file=prompts_file)

    # Read the content of the CV
    cv_content = ''
    try:
        # 1. Essai prioritaire avec UTF-8
        logger.info(f"Attempting to read file '{scr_file}' with UTF-8 encoding.")
        with open(scr_file, 'r', encoding='utf-8') as f:
            cv_content = f.read()
        logger.info(f"Successfully read file with UTF-8.")
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 decoding failed for '{scr_file}'. Attempting fallback with chardet.")
        try:
            # 2. Mécanisme de secours avec détection automatique
            with open(scr_file, 'rb') as f:
                raw_data = f.read()
            
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            
            if encoding:
                logger.info(f"Chardet detected encoding: '{encoding}'. Decoding with it.")
                cv_content = raw_data.decode(encoding)
                logger.info(f"Successfully read file with detected encoding '{encoding}'.")
            else:
                # 3. Erreur finale si la détection échoue
                logger.error(f"Chardet could not detect encoding for {scr_file}.")
                raise IOError(f"Unable to determine file encoding for {scr_file}.")
        except Exception as e:
            # 3. Erreur finale si le décodage de secours échoue
            logger.error(f"Fallback decoding also failed for {scr_file}. Error: {e}")
            raise IOError(f"Could not read file {scr_file}. Both UTF-8 and auto-detection failed.") from e

    # Read the JSON structure
    with open("../ressources/cv_structure.json", "r", encoding="utf-8") as f:
        json_structure = f.read()

    # Extract structured data from the CV
    response = agent.extract_cv_data(cv_content, json_structure)
    response = response.replace("```json", "").replace("```", "")
    logger.info(f"\nJSON complété :{response}")

    # --- PATCH: Check for empty or invalid JSON ---
    import json
    if not response.strip():
        raise ValueError("Erreur: le modèle LLM n'a pas renvoyé de données structurées. Veuillez vérifier le contenu du CV ou réessayer.")
    try:
        json.loads(response)
    except Exception as e:
        raise ValueError(f"Erreur: le modèle LLM a renvoyé un JSON invalide: {e}\nContenu reçu: {response[:200]}")
    # --- END PATCH ---

    # Determine the target file path
    if tgt_file == "":
        base_name = os.path.splitext(os.path.basename(scr_file))[0]
        tgt_file = f'../outputs/converted_{base_name}.json'

    logger.info(f"Attempting to write JSON to: {tgt_file}")

    # Write the response content to the target file
    try:
        with open(tgt_file, 'w', encoding='utf-8') as f:
            f.write(response)
        logger.info(f"JSON file written successfully to: {tgt_file}")
    except Exception as e:
        logger.error(f"Error writing JSON file: {str(e)}")
        raise

    return response

if __name__ == "__main__":
    # Configure command-line argument parsing
    parser = argparse.ArgumentParser(description="Extraction de données de CV avec LLM")
    parser.add_argument("cv_file", type=str, help="Chemin du fichier CV à traiter")
    parser.add_argument("--model", type=str, default="gpt-4o", help="Modèle LLM à utiliser (par défaut: gpt-3.5-turbo)")
    parser.add_argument("--test", type=str, default="", help="Test de la connexion de l'agent")
    parser.add_argument("--local", action="store_true", help="Utiliser un modèle local")
    args = parser.parse_args()

    # Test the LLM agent with the CV
    try:
        if args.cv_file:
            # Check if cv_file exists
            response = content_to_json(args.cv_file)
            if response is not None:
                logger.info(response)
            else:
                logger.info("Aucune réponse trouvée.")
        else:
            logger.error("Erreur : Fichier CV non spécifié. usage: python3 content_to_json.py --cv_file content.json")
    except FileNotFoundError:
        logger.error("Erreur : Fichier non trouvé (cv_court.txt ou cv_structure.json)")
    except ValueError as e:
        logger.error(f"Erreur : {str(e)}")
    except Exception as e:
        logger.error(f"Une erreur inattendue s'est produite : {str(e)}")