# /// script
# dependencies = [
#    "openai",
#    "python-dotenv",
#    "mistralai",
#    "google-generativeai",
#    "requests",
#    "chardet"
# ]
# ///
# To run this script, use the following command:
# uv llm_agent.py data_to_be_parsed.txt

import os
from typing import List, Dict, Optional
import openai
from dotenv import load_dotenv
import json
import argparse
from mistralai import Mistral
import google.generativeai as genai
import requests
import chardet
import inspect
import time
import traceback # Ajouté pour l'affichage des erreurs

class LLMAgent:
    # def __init__(self, model: str = "gemini-2.0-flash", local_model: bool = False):
    # def __init__(self, model: str = "gemini-2.0-flash-exp", local_model: bool = False):
    # def __init__(self, model: str = "gpt-4o-mini", local_model: bool = False):
    def __init__(self, model: str = "gpt-4o", local_model: bool = False, prompts_file="/home/steeve/cv_format/ressources/prompts.json"):
        """
        Initialise l'agent LLM.

        Args:
            model (str): Le modèle à utiliser (par défaut: gpt-3.5-turbo)
            local_model (bool): Indique si le modèle est local (par défaut: False)
            prompts_file (str): Path to the prompts JSON file (default: /home/steeve/cv_format/ressources/prompts.json)
        """
        # Charger les variables d'environnement
        load_dotenv()

        self.model = model
        self.local_model = local_model
        self.prompts_file = prompts_file
        load_dotenv()

        # Configurer l'API OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("La clé API OpenAI n'est pas définie dans le fichier .env")

        self.model = model
        self.local_model = local_model
        self.conversation_history: List[Dict] = []

        if model.startswith('gpt'):
            self.client = openai.OpenAI(api_key=api_key)
        elif model == "codestral":
            codestral_api_key = os.getenv("CODESTRAL_API_KEY")
            if not codestral_api_key:
                raise ValueError("La clé API Codestral n'est pas définie dans le fichier .env")
            self.client = self._configure_codestral_client(codestral_api_key)
        elif model.startswith('mistral'):
            mistral_api_key = os.getenv("MISTRAL_API_KEY")
            if not mistral_api_key:
                raise ValueError("La clé API Mistral n'est pas définie dans le fichier .env")
            self.client = Mistral(api_key=mistral_api_key)
        elif model.startswith("gemini"):
            gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not gemini_key:
                raise ValueError("API key for Gemini must be set in .env as GEMINI_API_KEY or GOOGLE_API_KEY")
            self.client = self._configure_gemini_client(gemini_key, model)
        else:
            raise ValueError(f"Unsupported model: {model}")

    def _configure_codestral_client(self, api_key: str):
        # Configurer le client Mistral
        return Mistral(api_key=api_key)

    def _configure_gemini_client(self, api_key: str, mname: str):
        # Implémentez la configuration du client Gemini ici
        # Par exemple, si Gemini utilise une bibliothèque spécifique
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(mname)

    def add_message(self, role: str, content: str):
        """
        Ajoute un message à l'historique de la conversation.

        Args:
            role (str): Le rôle du message ('system', 'user', ou 'assistant')
            content (str): Le contenu du message
        """
        self.conversation_history.append({"role": role, "content": content})

    def clear_history(self):
        """Efface l'historique de la conversation."""
        self.conversation_history = []

    def _call_gpt_with_retry(self, client: openai.OpenAI, model: str, messages: List[Dict], temperature: float, max_tokens: int) -> str:
        """
        Fonction d'assistance pour appeler l'API OpenAI avec une nouvelle tentative en cas de 'rate limit'.
        Attend 60 secondes avant de réessayer.
        """
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except openai.RateLimitError as e:
            print(f"\n--- ATTENTION: Le modèle OpenAI '{model}' a atteint une limite de débit. Attente de 60 secondes... ---")
            print(f"Détails de l'erreur: {e}")
            time.sleep(60)
            print(f"--- Nouvelle tentative d'appel à '{model}'... ---")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            print("--- Nouvelle tentative réussie ---")
            return response.choices[0].message.content

    def get_response(self,
                     prompt: str,
                     system_prompt: Optional[str] = None,
                     temperature: float = 0.2,
                     max_tokens: int = 16_000) -> str:
        """
        Envoie un prompt au LLM et retourne sa réponse.

        Args:
            prompt (str): Le message de l'utilisateur
            system_prompt (str, optional): Message système pour définir le comportement du LLM
            temperature (float): Contrôle la créativité des réponses (0.0 à 2.0)
            max_tokens (int): Nombre maximum de tokens dans la réponse

        Returns:
            str: La réponse du LLM
        """
        messages = []

        # Ajouter le message système si fourni
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Ajouter l'historique de la conversation
        # messages.extend(self.conversation_history)

        # Ajouter le nouveau prompt
        messages.append({"role": "user", "content": prompt})

        try:
            if self.local_model:
                # Appeler le modèle local
                response = requests.post(
                    "http://127.0.0.1:1234/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                response.raise_for_status()
                assistant_response = response.json()["choices"][0]["message"]["content"]
            elif self.model.startswith('gpt'):
                # Appeler l'API OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                # Extraire la réponse
                assistant_response = response.choices[0].message.content
            elif self.model == "codestral":
                # Appeler l'API Mistral
                response = self.client.chat.complete(
                    model="mistral-large-latest",
                    messages=messages
                )
                # Extraire la réponse
                assistant_response = response.choices[0].message.content
            elif self.model.startswith("gemini"):
                try: 
                    # Formatter les messages pour Gemini
                    try:
                        # Combiner system_prompt et prompt pour Gemini
                        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

                        response = self.client.generate_content(
                            contents=[{"parts": [{"text": full_prompt}]}],
                            generation_config=genai.types.GenerationConfig(
                                temperature=temperature,
                                max_output_tokens=max_tokens,
                                response_mime_type="text/plain" # "application/json"
                            )
                        )

                        # Debug print to check the response structure
                        # print("Gemini API Response:", response)

                        # Valider la structure de la réponse de manière exhaustive
                        if not getattr(response, 'candidates', None):
                            raise ValueError("Aucun candidat dans la réponse Gemini")

                        first_candidate = response.candidates[0]
                        if not getattr(first_candidate, 'content', None):
                            raise ValueError("Contenu de réponse vide dans le candidat Gemini")

                        content_parts = getattr(first_candidate.content, 'parts', [])
                        if not content_parts:
                            raise ValueError("Aucune partie de contenu dans la réponse Gemini")

                        # Accès sécurisé au texte de réponse
                        assistant_response = getattr(content_parts[0], 'text', '')
                        if not assistant_response:
                            raise ValueError("Réponse texte vide dans la partie de contenu Gemini")

                    except AttributeError as e:
                        raise RuntimeError(f"Structure de réponse Gemini invalide: {str(e)}") from e
                    except Exception as e:
                        raise RuntimeError(f"Erreur Gemini API: {str(e)}") from e
                except Exception as gemini_error:
                    print(f"\n--- ATTENTION: L'appel à l'API Gemini a échoué: {gemini_error} ---")
                    print("--- Basculement vers le modèle de secours 'gpt-4o' ---")
                    try:
                        api_key = os.getenv("OPENAI_API_KEY")
                        if not api_key:
                            raise ValueError("La clé API OpenAI est requise pour le modèle de secours 'gpt-4o'")
                        
                        fallback_client = openai.OpenAI(api_key=api_key)
                        
                        assistant_response = self._call_gpt_with_retry(
                            client=fallback_client,
                            model="gpt-4o",
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        print("--- Basculement vers 'gpt-4o' réussi ---\n")
                    except Exception as fallback_error:
                        print(f"--- Le modèle de secours 'gpt-4o' a également échoué: {fallback_error} ---")
                        raise RuntimeError("L'appel à Gemini et au modèle de secours gpt-4o ont tous deux échoué.") from fallback_error
            else:
                raise ValueError(f"Modèle non supporté: {self.model}")

            # Mettre à jour l'historique
            self.add_message("user", prompt)
            self.add_message("assistant", assistant_response)

            return assistant_response

        except Exception as e:
            # Find the original caller of the API call to provide better context in errors.
            stack = inspect.stack()
            caller_function = "Unknown"
            caller_filename = "Unknown"
            caller_lineno = "Unknown"

            # Iterate up the stack to find the first call outside of this file (llm_agent.py).
            # This helps to ignore internal wrappers like get_response_without_history.
            try:
                current_filename = os.path.basename(__file__)
                for frame_info in stack:
                    frame_filename = os.path.basename(frame_info.filename)
                    if frame_filename != current_filename:
                        caller_function = frame_info.function
                        caller_filename = frame_filename
                        caller_lineno = frame_info.lineno
                        break
                else:
                    # Fallback if the entire call stack is within this file
                    if len(stack) > 1:
                        caller_frame = stack[1]
                        caller_function = caller_frame.function
                        caller_filename = os.path.basename(caller_frame.filename)
                        caller_lineno = caller_frame.lineno
            except Exception as inspect_error:
                # In case of any issue with inspection, we don't want to crash.
                print(f"Error during stack inspection: {inspect_error}")

            # Construct a more informative error message
            error_context = (
                f"Erreur lors de l'appel à l'API pour le modèle '{self.model}'\n"
                f"-> Appelant: {caller_function}() dans {caller_filename}:{caller_lineno}"
            )
            
            # Log the detailed error and traceback for debugging
            print(f"\n--- ERREUR LLM AGENT ---")
            print(error_context)
            print(f"Détails de l'erreur: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            print(f"------------------------\n")

            # Return a user-friendly but informative error message
            return f"{error_context}\nDétails: {str(e)}"

    def get_response_without_history(self,
                                     prompt: str,
                                     system_prompt: Optional[str] = None,
                                     temperature: float = 0.1,
                                     max_tokens: int = 16_000) -> str:
        """
        Envoie un prompt unique au LLM sans conserver l'historique.

        Args:
            prompt (str): Le message de l'utilisateur
            system_prompt (str, optional): Message système pour définir le comportement du LLM
            temperature (float): Contrôle la créativité des réponses (0.0 à 2.0)
            max_tokens (int): Nombre maximum de tokens dans la réponse

        Returns:
            str: La réponse du LLM
        """
        current_history = self.conversation_history.copy()
        self.clear_history()
        response = self.get_response(prompt, system_prompt, temperature, max_tokens)
        self.conversation_history = current_history
        return response

    def extract_cv_data(self, cv_content: str, json_structure: dict) -> str:
        """
        Extrait les données d'un CV à partir d'un document HTML en déroulant 7 prompts successifs :
        1. Extraction et nettoyage du contenu HTML
        2. Segmentation et identification des sections du CV
        3. Extraction détaillée et structuration dans le JSON cible
        4. Validation et fusion du JSON (correction des incohérences éventuelles)
        5. Génération du résumé du parcours professionnel en 5 lignes (si champ vide)
        6. Complétion des maîtrises fonctionnelles principales en 5 lignes (si champ vide)
        7. Formatage des champs "contexte de la mission" et "taches" (séparation par '#')

        Args:
            cv_content (str): Le contenu HTML du CV.
            json_structure (dict): La structure JSON à remplir.

        Returns:
            str: Le JSON complété et post-traité.
        """
        # Load prompts from JSON file
        with open(self.prompts_file, "r", encoding="utf-8") as f:
            prompts = json.load(f)
        
        content = cv_content
        for index, prompt_info in enumerate(prompts[1:], 1):
            print(f'phase {index}')
            condition = prompt_info.get("condition")
            if condition: 
                try: 
                    formatted_condition = condition.format(cv_content=repr(content)) 
                    if not eval(formatted_condition):
                        print(f"Phase {index} skipped as the condition is not met.")
                        continue
                except Exception as e:
                    print(f"Warning: Failed to evaluate condition for phase {index}. Erreur {e}. Executing the step by default.")
                    with open(f'/home/steeve/cv_format/outputs/phase{index}_log.txt', 'w', encoding='utf-8') as log_file:
                        log_file.write(f"Condition evaluation failed for phase {index}. Error: {e}\n")
                        log_file.write(f"{formatted_condition}")
                    print(f'Log written for phase {index} in {log_file.name}')
                    print(f'Log file path: /home/steeve/cv_format/outputs/phase{index}_log.txt')
            system_prompt = prompt_info["system_prompt"]
            prompt_template = prompt_info["prompt"]
            prompt = prompt_template.format(cv_content=content, json_structure=json_structure)
            # print(prompt)
            # print("-------------------------------------------")
            
            response = self.get_response_without_history(prompt=prompt, system_prompt=system_prompt, temperature=0.1)
            # print(response)
            response = response.replace("```json", "").replace("```", "")
            with open(f'/home/steeve/cv_format/outputs/trace{index}.txt', 'w', encoding='utf-8') as f:
                f.write(response)

            # Ensure the response is properly formatted
            try:
                response_json = json.loads(response)
                content = json.dumps(response_json, ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                content = response
        
        final_response = content
        # Écrire final_response dans un fichier de trace pour le débogage
        with open('/home/steeve/cv_format/outputs/trace.txt', 'w', encoding='utf-8') as f:
            f.write(final_response)
            
        # Validation du JSON final
        try:
            json.loads(final_response)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", str(e))
            return f"Erreur lors de l'extraction des données du CV: {str(e)}"

        return final_response

if __name__ == "__main__":
    # Configurer l'analyse des arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Extraction de données de CV avec LLM")
    parser.add_argument("cv_file", type=str, help="Chemin du fichier CV à traiter")
    parser.add_argument("--model", type=str, default="gpt-4o", help="Modèle LLM à utiliser (par défaut: gpt-3.5-turbo)")
    parser.add_argument("--test", type=str, default="", help="Test de la connexion de l'agent")
    parser.add_argument("--local", action="store_true", help="Utiliser un modèle local")
    args = parser.parse_args()

    # Test de l'agent LLM avec le CV
    try:
        # Créer une instance de l'agent
        # print(args.model)
        # print(args.test)
        agent = LLMAgent(model=args.model, local_model=args.local)

        if args.test != "":
            print(agent.get_response_without_history("capitale de la france ?"))
            quit()

        # Lire le contenu du CV
        encoding = ''
        with open(args.cv_file, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        print(f"Detected encoding: {encoding}")

        # read the actual file with the right format
        with open(args.cv_file, "r", encoding=encoding) as f:
            cv_content = f.read()

        # Lire la structure JSON
        with open("/home/steeve/cv_format/ressources/cv_structure.json", "r", encoding="utf-8") as f:
            json_structure = f.read()

        # Test 1 : Extraction structurée des données du CV
        response = agent.extract_cv_data(cv_content, json_structure)
        response = response.replace("```json", "").replace("```", "")
        print("\nJSON complété :")
        print(response)

        # response content to r'Z:\CVs\cv_content.json'
        with open('/home/steeve/cv_format/outputs/cv_content.json', 'w', encoding='utf-8') as f:
            f.write(response)

    except FileNotFoundError:
        print("Erreur : Fichier non trouvé (cv_court.txt ou cv_structure.json)")
    except ValueError as e:
        print(f"Erreur : {str(e)}")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {str(e)}")