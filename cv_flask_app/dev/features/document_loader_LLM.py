#!/usr/bin/env python3
"""
Document Loader CLI v3 - Extraction intelligente + post-traitement LLM
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
import re
import unicodedata
#from .llm_agent import LLMAgent

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.partition.docx import partition_docx
    from unstructured.partition.doc import partition_doc
    from unstructured.documents.elements import Element
except ImportError:
    print("Erreur: Installez les dépendances avec:")
    print("pip install 'unstructured[pdf,docx]' python-magic-bin")
    sys.exit(1)

try:
    from .llm_agent import LLMAgent
except ImportError:
    print("Erreur: Module LLMAgent non trouvé")
    print("Assurez-vous que features/llm_agent.py est accessible")
    sys.exit(1)


class SmartDocumentLoaderWithLLM:
    """Gestionnaire de chargement intelligent avec post-traitement LLM"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc'}
    
    def __init__(self, use_llm: bool = True, llm_model: str = "gpt-4o"):
        self.use_llm = use_llm
        self.llm_model = llm_model
        self.partitioners = {
            '.pdf': partition_pdf,
            '.docx': partition_docx,
            '.doc': partition_doc
        }
        
        # Initialisation de l'agent LLM si nécessaire
        if self.use_llm:
            try:
                self.llm_agent = LLMAgent(self.llm_model)
            except Exception as e:
                print(f"Attention: Impossible d'initialiser le LLM ({e})")
                print("Extraction sans post-traitement LLM")
                self.use_llm = False
    
    def load_document(self, file_path: str) -> str:
        """Charge un document avec extraction intelligente et post-traitement LLM"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        extension = path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Format non supporté: {extension}")
        
        # Étape 1: Extraction avec unstructured
        try:
            partitioner = self.partitioners[extension]
            if extension == '.doc':
                elements = partitioner(filename=str(path), outputencoding='utf-8')
            else:
                elements = partitioner(filename=str(path))
            raw_content = self._extract_raw_content(elements)
            # print(raw_content)
            
            caracteres_a_remplacer = [
                re.escape('\u2022'),  # •
                re.escape('\u2023'),  # ‣
                re.escape('\u25E6'),  # ◦
                re.escape('\u25AA'),  # ▪
                re.escape('\u25AB'),  # ▫
                re.escape('\u25BA'),  # ►
                re.escape('\u25B8'),  # ▸
                re.escape('\u25B9'),  # ➢
                re.escape('\u25BB'),  # ▻
                re.escape('\u25A0'),  # ■
                re.escape('\u25A1'),  # □
                re.escape('\u2591'),  # ░
                re.escape('\u2592'),  # ▒
                re.escape('\u2593'),  # ▓
                re.escape('\u25CF'),  # ●
                re.escape('\uF015'),  # 
                re.escape('\uF0A7'),  # 
                re.escape('\uF0D8'),  # 
                re.escape('\uF0E0'),  # 
                re.escape('\uF0E0'),  # 
                re.escape('\uF1B9'),  # 
                re.escape('\uF2BB'),  # 
                re.escape('\uF87B'),  # 
                re.escape('\uFFFD'),  # �
                re.escape('\U0001F4A1'),  # 💡
                re.escape('\U0001F4C4'),  # 📄
                re.escape('\U0001F539'),  # 🔹
                re.escape('\U0001F6E0'),  # 🛠
                re.escape('\U0001F30D'),  # 🌍
                re.escape('\U0001F396'),  # 🎖
                re.escape('\U0001F3C6'),  # 🏆
                re.escape('\U0001F3A4'),  # 🎤
                re.escape('\U0001267B'),  # ♻
                re.escape('\U0001F4DD'),  # 📝
                re.escape('\U0001F31F'),  # 🌟
                re.escape('\U0001F3BD'),  # 🎽
                re.escape('\u26F5'),  # ⛵
                re.escape('\U0001F3E0'),  # 🏠
                re.escape('\U000F0943'),  # 󰥃
            ]
            pattern = r'[' + ''.join(caracteres_a_remplacer) + ']'
            print(f"Regex pattern: {pattern}")
            raw_content = re.sub(pattern, '\n', raw_content)
            # raw_content = re.sub('(\r?\n|\r){3,}', '\n\n', raw_content)
            print("Special characters replaced")
            print(f"Use a LLM after extraction? {self.use_llm}")
            
            # doubles caractères ?
            raw_content = raw_content.replace('\uFB01', 'fi').replace('\uFB02', 'fl').replace('\uFB00', 'ff')
            raw_content = raw_content.replace('\uFB03', 'ffi').replace('\uFB04', 'ffl')
            raw_content = raw_content.replace('\uFB05', 'st').replace('\uFB06', 'st').replace('\uFB07', 'tz').replace('\uFB08', 'ct')
            raw_content = raw_content.replace('\t', '    ')
            return raw_content

            if not self.use_llm:
                return raw_content

            print(f'content before LLM call : \n{raw_content}')
            
            # Étape 2: Post-traitement avec LLM
            processed_content = self._process_with_llm(raw_content)
            print('=========================================')
            print(repr(processed_content))
            print('=========================================')
            return f'OK\n{processed_content}'
            
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'extraction: {e}")
    
    def _extract_raw_content(self, elements: List[Element]) -> str:
        """Extrait le contenu brut des éléments"""
        content_parts = []
        
        for element in elements:
            if not element.text or not element.text.strip():
                continue
                
            # element_type = type(element).__name__
            text = element.text.strip()
            
            # Marquage simple selon le type d'élément
            # if element_type == "Title":
            #    content_parts.append(f"[TITRE] {text}")
            # elif element_type == "ListItem":
            #     content_parts.append(f"[LISTE] {text}")
            # elif element_type == "Table":
            #     content_parts.append(f"[TABLEAU] {text}")
            # else:
            #     content_parts.append(text)
            content_parts.append(text)
        
        return "\n".join(content_parts)
    
    def _process_with_llm(self, raw_content: str) -> str:
        """Post-traite le contenu avec un LLM pour améliorer la structure"""
        
        system_prompt = """Tu es un expert en restructuration de documents. 
Ton rôle est de prendre un texte extrait d'un PDF et de le réorganiser de façon logique et lisible.
Instructions :
1. Reconstitue les listes et énumérations de façon cohérente. 
2. Préserve tout le contenu. On doit le retrouver intégralement dans le résultat final.
3. Retourne uniquement le texte restructuré, sans commentaires ni explications, et surtout pas au format JSON.

Retourne uniquement le texte restructuré, sans commentaires ni explications."""
        system_prompt = """
IMPORTANT : RÉPONDS UNIQUEMENT EN TEXTE BRUT, SANS AUCUN FORMATAGE (PAS DE JSON, PAS DE LISTES, PAS D’ACCOLADES, PAS DE CROCHETS).

Ta tâche :
Si des informations sont sur plusieurs colonnes mais liées (ex : année + diplôme), garde-les ensemble sur une seule ligne.
Si des parties du texte sont séparées en colonnes mais concernent des thèmes différents, regroupe chaque thème dans un paragraphe complet avant de passer au suivant.
Conserve la présentation en chapitres et blocs de texte.
Tout le contenu initial doit se retrouver intégralement dans le résultat final. Ne résume pas le contenu.
Si des informations sont sur plusieurs colonnes mais liées (ex : année + diplôme), garde-les ensemble sur une seule ligne.
Si des parties du texte sont séparées en colonnes mais concernent des thèmes différents, regroupe chaque thème dans un paragraphe complet avant de passer au suivant.
Les listes doivent être présentées de façon cohérente (par exemple, les caractères '•' doivent être en début de ligne)
Préserve tout le contenu, sans rien omettre.
Le résultat doit être un texte sans aucun formatage particulier."""

        try:
            processed_content = self.llm_agent.get_response_without_history(
                raw_content, 
                system_prompt
            )
            # print(f"processed_content before strip: {repr(processed_content)}")
            return processed_content.strip()
            
        except Exception as e:
            print(f"Attention: Erreur lors du post-traitement LLM: {e}")
            print("Retour du contenu brut")
            return raw_content
    
    def save_text(self, content: str, output_path: str) -> None:
        """Sauvegarde le contenu dans un fichier texte"""
        with open(output_path, 'w', encoding='utf-8') as f:
            # f.write(content.replace('\\n', '\n'))
            f.write(content)
    
    def get_document_info(self, file_path: str) -> dict:
        """Retourne des informations sur le document"""
        path = Path(file_path)
        extension = path.suffix.lower()
        partitioner = self.partitioners[extension]
        
        elements = partitioner(filename=str(path))
        
        element_types = {}
        total_chars = 0
        
        for element in elements:
            element_type = type(element).__name__
            element_types[element_type] = element_types.get(element_type, 0) + 1
            if element.text:
                total_chars += len(element.text)
        
        return {
            'total_elements': len(elements),
            'element_types': element_types,
            'total_characters': total_chars,
            'file_size': path.stat().st_size,
            'llm_enabled': self.use_llm,
            'llm_model': self.llm_model if self.use_llm else None
        }

call = False

def main():
    global call
    parser = argparse.ArgumentParser(
        description="Extraction intelligente + post-traitement LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python document_loader_v3.py document.pdf output.txt
  python document_loader_v3.py --no-llm rapport.docx contenu.txt
  python document_loader_v3.py --model gpt-4o document.pdf output.txt
  python document_loader_v3.py --info document.pdf
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Chemin vers le document à traiter (PDF, DOC, DOCX)'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        help='Chemin vers le fichier texte de sortie'
    )
    
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Désactive le post-traitement LLM'
    )
    
    parser.add_argument(
        '--model',
        default='gpt-4o',
        help='Modèle LLM à utiliser (défaut: gemini-1.5-pro)'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Affiche uniquement les informations sur le document'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mode verbeux'
    )
    
    parser.add_argument(
        '--call',
        action='store_true',
        help='Return 0 on success, actual return code on failure'
    )
    
    args = parser.parse_args()
    
    try:
        if args.call: call = True
        return_code = 0  # Initialize return_code
        loader = SmartDocumentLoaderWithLLM(
            use_llm=not args.no_llm,
            llm_model=args.model
        )
        
        # Mode information uniquement
        if args.info:
            info = loader.get_document_info(args.input_file)
            print(f"📄 Analyse de: {args.input_file}")
            print(f"   Taille: {info['file_size']:,} octets")
            print(f"   Éléments: {info['total_elements']}")
            print(f"   Caractères: {info['total_characters']:,}")
            print(f"   LLM activé: {'✅' if info['llm_enabled'] else '❌'}")
            if info['llm_enabled']:
                print(f"   Modèle: {info['llm_model']}")
            print("   Types d'éléments:")
            for elem_type, count in info['element_types'].items():
                print(f"     - {elem_type}: {count}")
            return
        
        if not args.output_file:
            parser.error("Le fichier de sortie est requis (sauf avec --info)")
        
        if args.verbose:
            print(f"🔍 Extraction de: {args.input_file}")
            if not args.no_llm:
                print(f"   Post-traitement LLM: {args.model}")
            else:
                print("   Post-traitement LLM: désactivé")
        
        # Extraction du contenu
        content = loader.load_document(args.input_file)
        
        if args.verbose:
            print(f"   Contenu final: {len(content):,} caractères")
        
        # Sauvegarde
        loader.save_text(content, args.output_file)
        
        if args.verbose:
            print(f"✅ Sauvegardé dans: {args.output_file}")
        else:
            print("✅ Extraction et post-traitement terminés")
            
    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        return_code = 1  # Set return_code to 1 on exception
    finally:
        if args.call:
            sys.exit(return_code)


if __name__ == "__main__":
    main()
def document_loader(input_file: str, output_file: str, model: Optional[str] = None) -> None:
    """
    Loads a document, extracts content, and saves it to a file.
    Optionally uses an LLM for post-processing.

    Args:
        input_file: Path to the input document.
        output_file: Path to the output text file.
        model: Optional LLM model to use for post-processing. If None, no LLM is used.
    """
    # loader = SmartDocumentLoaderWithLLM(use_llm=(model is not None), llm_model=model)
    loader = SmartDocumentLoaderWithLLM(use_llm=False)
    # loader = SmartDocumentLoaderWithLLM(use_llm=model is not None, llm_model=model)
    content = loader.load_document(input_file)
    print(repr(content))
    loader.save_text(content, output_file)