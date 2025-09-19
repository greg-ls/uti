#!/usr/bin/env python3
"""
Document Loader CLI v2 - Extraction intelligente avec unstructured
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.partition.docx import partition_docx
    from unstructured.partition.doc import partition_doc
    from unstructured.documents.elements import Element
except ImportError:
    print("Erreur: Installez les dépendances avec:")
    print("pip install 'unstructured[pdf,docx]' python-magic-bin")
    sys.exit(1)


class SmartDocumentLoader:
    """Gestionnaire de chargement intelligent de documents"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc'}
    
    def __init__(self, preserve_structure: bool = True):
        self.preserve_structure = preserve_structure
        self.partitioners = {
            '.pdf': partition_pdf,
            '.docx': partition_docx,
            '.doc': partition_doc
        }
    
    def load_document(self, file_path: str) -> str:
        """Charge un document avec extraction intelligente"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        extension = path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Format non supporté: {extension}")
        
        # Sélection du partitionneur approprié
        partitioner = self.partitioners[extension]
        
        try:
            # Extraction avec unstructured
            elements = partitioner(filename=str(path))
            
            if self.preserve_structure:
                content = self._format_with_structure(elements)
            else:
                content = self._format_simple(elements)
            
            return content
            
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'extraction: {e}")
    
    def _format_with_structure(self, elements: List[Element]) -> str:
        """Formate le contenu en préservant la structure logique"""
        formatted_lines = []
        
        for element in elements:
            if not element.text or not element.text.strip():
                continue
                
            element_type = type(element).__name__
            text = element.text.strip()
            
            # Formatage selon le type d'élément
            if element_type == "Title":
                formatted_lines.append(f"\n# {text}\n")
            elif element_type == "NarrativeText":
                # Paragraphe normal - on nettoie les sauts de ligne
                clean_text = self._clean_paragraph(text)
                formatted_lines.append(f"{clean_text}\n")
            elif element_type == "ListItem":
                formatted_lines.append(f"• {text}")
            elif element_type == "Table":
                formatted_lines.append(f"\n[TABLE]\n{text}\n")
            else:
                # Autres éléments (Header, Footer, etc.)
                clean_text = self._clean_paragraph(text)
                formatted_lines.append(f"{clean_text}")
        
        return "\n".join(formatted_lines)
    
    def _format_simple(self, elements: List[Element]) -> str:
        """Formatage simple sans structure"""
        texts = []
        for element in elements:
            if element.text and element.text.strip():
                clean_text = self._clean_paragraph(element.text.strip())
                texts.append(clean_text)
        
        return "\n\n".join(texts)
    
    def _clean_paragraph(self, text: str) -> str:
        """Nettoie un paragraphe en fusionnant les lignes cassées"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Si la ligne précédente se termine par un mot incomplet
            # et que la ligne courante commence par une minuscule,
            # on les fusionne
            if (cleaned_lines and 
                not cleaned_lines[-1].endswith(('.', '!', '?', ':', ';')) and
                line and line[0].islower()):
                cleaned_lines[-1] += " " + line
            else:
                cleaned_lines.append(line)
        
        return " ".join(cleaned_lines)
    
    def save_text(self, content: str, output_path: str) -> None:
        """Sauvegarde le contenu dans un fichier texte"""
        with open(output_path, 'w', encoding='utf-8') as f:
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
            'file_size': path.stat().st_size
        }


def main():
    parser = argparse.ArgumentParser(
        description="Extraction intelligente de documents PDF/Word avec unstructured",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python smart_loader.py document.pdf output.txt
  python smart_loader.py --no-structure rapport.docx contenu.txt
  python smart_loader.py --info document.pdf
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
        '--no-structure',
        action='store_true',
        help='Extraction simple sans préservation de structure'
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
    
    args = parser.parse_args()
    
    try:
        loader = SmartDocumentLoader(preserve_structure=not args.no_structure)
        
        # Mode information uniquement
        if args.info:
            info = loader.get_document_info(args.input_file)
            print(f"📄 Analyse de: {args.input_file}")
            print(f"   Taille: {info['file_size']:,} octets")
            print(f"   Éléments: {info['total_elements']}")
            print(f"   Caractères: {info['total_characters']:,}")
            print("   Types d'éléments:")
            for elem_type, count in info['element_types'].items():
                print(f"     - {elem_type}: {count}")
            return
        
        if not args.output_file:
            parser.error("Le fichier de sortie est requis (sauf avec --info)")
        
        if args.verbose:
            print(f"🔍 Extraction de: {args.input_file}")
            mode = "avec structure" if not args.no_structure else "simple"
            print(f"   Mode: {mode}")
        
        # Extraction du contenu
        content = loader.load_document(args.input_file)
        
        if args.verbose:
            print(f"   Contenu extrait: {len(content):,} caractères")
        
        # Sauvegarde
        loader.save_text(content, args.output_file)
        
        if args.verbose:
            print(f"✅ Sauvegardé dans: {args.output_file}")
        else:
            print("✅ Extraction terminée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()