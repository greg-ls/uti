# /// script
# dependencies = [
#     "python-docx",
#     "argparse"
# ]
# ///
# To run this script, use the following command:
# uv word_interact.py

import json
from pickle import TRUE
from docx import Document
import os
from docx.shared import Inches, RGBColor, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, ns
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
import re


def set_table_indent(table, indent):
    """
    Définit un retrait du tableau pour déplacer l'icône.

    Args:
        table (Table): Le tableau Word.
        indent (float): Valeur du retrait (négatif pour aller à gauche).
    """
    tbl = table._tbl  # Accès à l'élément XML du tableau
    tblPr = tbl.get_or_add_tblPr()
    
    tblInd = OxmlElement('w:tblInd')
    tblInd.set(ns.qn('w:w'), str(int(indent * 1440)))  # Conversion en Twips
    tblInd.set(ns.qn('w:type'), 'dxa')
    
    tblPr.append(tblInd)

def add_section_with_icon(doc, icon_path, title, style="Heading1", indent=-0.3):
    """
    Ajoute une section avec une icône décalée à gauche et le texte bien aligné.

    Args:
        doc (Document): Le document Word.
        icon_path (str): Chemin de l'icône à insérer.
        title (str): Titre de la section.
        style (str): Style du titre.
        indent (float): Déplacement horizontal du tableau (négatif = vers la gauche).
    """
    table = doc.add_table(rows=1, cols=2)
    
    # Définir un retrait négatif pour que l'icône dépasse à gauche
    set_table_indent(table, Inches(indent))

    # Récupérer les cellules du tableau
    cell_icon = table.cell(0, 0)
    cell_text = table.cell(0, 1)
    
    # Définir la largeur des colonnes
    cell_icon.width = Inches(0.6)  # Petite colonne pour l'icône
    cell_text.width = Inches(5.5)  # Large colonne pour le texte

    # Ajouter l'icône dans la cellule de gauche
    if os.path.exists(icon_path):
        paragraph = cell_icon.paragraphs[0]
        run = paragraph.add_run()
        run.add_picture(icon_path, width=Inches(0.4))  # Ajuste la taille de l'image
    else:
        print(f"Image non trouvée : {icon_path}")

    # Ajouter le titre formaté dans la cellule de droite
    paragraph = cell_text.paragraphs[0]
    run = paragraph.add_run(title)
    run.bold = True  # Texte en gras
    paragraph.style = style

# export data avec le style STYLE
def export_data(data, style, doc):
        current_paragraph = doc.add_paragraph(data)
        current_paragraph.style = style

def export_trimed_data(data, style, doc):
        trimmed_data = data.strip()
        current_paragraph = doc.add_paragraph(trimmed_data)
        current_paragraph.style = style

def separation(msg, doc):
    current_paragraph = doc.add_paragraph(msg)
    current_paragraph.style = 'SEPARATION'

def populate_word(content):
    """Generate a basic word document from text content"""
    doc = Document()
    for line in content.split('\n'):
        current_paragraph = doc.add_paragraph(line)
        current_paragraph.style = 'Normal'
    if os.path.exists(r'C:\Users\steev\OneDrive\scripts\UTI\CV\cv_content.docx'):
        os.remove(r'C:\Users\steev\OneDrive\scripts\UTI\CV\cv_content.docx')
    doc.save(r'C:\Users\steev\OneDrive\scripts\UTI\CV\cv_content.docx')

def get_data(field, src):
    """
    Retrieves the content of a given field from a JSON object.

    Args:
        field (str): The name of the field to retrieve.
        src (dict): The JSON object to retrieve the data from.

    Returns:
        str: The content of the field, or an empty string if the field is not found.
    """
    try:
        return str(src.get(field, ""))
    except:
        return ""

def add_markdown_bold_paragraph(doc, text, style=None):
    """
    Add a paragraph to the doc with Markdown-style bold (**text** or __text__) converted to Word bold.
    """
    paragraph = doc.add_paragraph(style=style)
    # Regex to split text into bold and non-bold parts
    # Matches **bold** or __bold__
    pattern = re.compile(r'(\*\*|__)(.+?)\1')
    pos = 0
    for match in pattern.finditer(text):
        # Add text before bold
        if match.start() > pos:
            paragraph.add_run(text[pos:match.start()])
        # Add bold text
        bold_text = match.group(2)
        run = paragraph.add_run(bold_text)
        run.bold = True
        pos = match.end()
    # Add remaining text after last bold
    if pos < len(text):
        paragraph.add_run(text[pos:])
    return paragraph

def generate_word_new_template(source_json, target_template):
    """Generate a Word document from a JSON source and a template.
    This function takes a JSON object as input and generates a Word document
    based on a specified template. The JSON object should contain the data
    to be inserted into the Word document, and the template should be a path
    to a Word document (.docx) that acts as a base for the generated document.

    Args:
        source_json (_type_): _description_
        target_template (_type_): _description_
    """

    doc = Document(target_template)
    with open(source_json, 'r', encoding='utf-8') as file:
        src = json.load(file)
    
    temp = get_data("denomination_du_poste_recherche", src)

def aptos_10(run):
    run.font.name = "Aptos"
    run.font.size = Pt(10)

def aptos_11(run):
    run.font.name = "Aptos"
    run.font.size = Pt(11)

def generate_word_new(source_json, target_template, output_path, input_file_path=None):
    """Generate a Word document from a JSON source and a template.
    This function takes a JSON object as input and generates a Word document
    based on a specified template. The JSON object should contain the data
    to be inserted into the Word document, and the template should be a path
    to a Word document (.docx) that acts as a base for the generated document.

    Args:
        source_json (str): Path to the source JSON file
        target_template (str): Path to the Word template file
        output_path (str): Path where the generated Word file should be saved
        input_file_path (str, optional): Additional input file path
    """
    """Generate a Word document from a JSON source and a template.
    This function takes a JSON object as input and generates a Word document
    based on a specified template. The JSON object should contain the data
    to be inserted into the Word document, and the template should be a path
    to a Word document (.docx) that acts as a base for the generated document.

    Args:
        source_json (_type_): _description_
        target_template (_type_): _description_
    """
    
    doc = None

    if target_template:  # If template is provided, use it
        doc = Document(target_template)
    else:  # Otherwise create a new document
        doc = Document()

    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Aptos'
    font.size = Pt(10)

    with open(source_json, 'r', encoding='utf-8') as file:
        src = json.load(file)
    
    temp = get_data("denomination_du_poste_recherche", src)
    if temp == "": temp = get_data("dénomination du poste recherché", src)
    
    try:
        doc.add_paragraph(f"{temp}", style="poste_recherche")
    except:
        doc.add_paragraph(f"{temp}", style="POSTE_RECHERCHE")
    
    doc.add_paragraph("SYNTHESE DES COMPETENCES", style="section")
    
    temp = get_data("resume_du_parcours_professionnel_en_5_lignes", src)
    if temp != "":
        doc.add_paragraph(temp, "Normal")
        doc.add_paragraph(' ', style="Normal")
    else : 
        oc.add_paragraph(' ', style="Normal")
    
    doc.add_paragraph("EXPÉRIENCES", style="section")
    
    for xp in src['experience']:
        entreprise, debut, fin = xp['entreprise'], xp['date_debut'], xp['date_fin']
        poste = xp['poste_occupe']

        t = doc.add_table(rows=1, cols=2)
        for row in t.rows: # ;)
            row.cells[0].width = Cm(11)
            row.cells[1].width = Cm(6)

        t.autofit = False
        tbl = t._tbl
        tblPr = tbl.tblPr
        tblCellMar = tblPr.find(qn('w:tblCellMar'))
        if tblCellMar is None:
            tblCellMar = OxmlElement('w:tblCellMar')
            tblPr.append(tblCellMar)

        # for margin in ('top', 'left', 'bottom', 'right'):
        mar = tblCellMar.find(qn(f'w:{'left'}'))
        if mar is None:
            mar = OxmlElement(f'w:{'left'}')
            tblCellMar.append(mar)
        mar.set(qn('w:w'), '0')
        mar.set(qn('w:type'), 'dxa')

        c_left = t.cell(0, 0)
        p = c_left.paragraphs[0]
        r = p.add_run(f"{entreprise} - ")
        r.bold = True
        aptos_11(r)
        r = p.add_run(f"{poste}")
        r.bold = True
        r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
        aptos_11(r)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        c_right = t.cell(0, 1)
        p = c_right.paragraphs[0]
        r = p.add_run(f"{debut} - {fin}")
        r.bold = True
        aptos_11(r)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # doc.add_paragraph(' ', style="Normal")

        if xp['contexte de la mission']:           
            ctxt = xp['contexte de la mission']
            p = doc.add_paragraph()
            r = p.add_run('Project : ')
            r.bold = True
            if '#' in ctxt:
                parts = ctxt.split('#')
                r = p.add_run(parts[0].strip())
                for part in parts[1:]:
                    if part.strip():
                        r = r.add_break()
                        r = p.add_run(f"{part.strip()}")
            else:
                p.add_run(f"{ctxt}")

        taches = xp['taches']
        if taches:
            for t in taches.split('#'):
                p = doc.add_paragraph(style="puce_1")
                r = p.add_run(f"❖ ")
                r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
                p.add_run(f"{t}")

        # doc.add_paragraph(' ', style="Normal")

        env = xp['environnement_technique']
        if env:
            p = doc.add_paragraph()
            r = p.add_run(f'{env}')
            r.bold = True
            r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

        doc.add_paragraph(' ', style="Normal")

    doc.add_paragraph("COMPÉTENCES", style="section")
    
    temp = get_data("competences fonctionnelles", src)    
    if temp != "":
        for sub in temp.split('#'):
            if sub.strip():
                p = doc.add_paragraph(style="puce_1")
                r = p.add_run(f"❖ ")
                r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
                r = p.add_run(sub.strip())

    temp = get_data("competences techniques", src)    
    if temp != "":
        for sub in temp.split('#'):
            if sub.strip():
                p = doc.add_paragraph(style="puce_1")
                r = p.add_run(f"❖ ")
                r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
                r = p.add_run(sub.strip())    
    
    doc.add_paragraph(" ")
    p = doc.add_paragraph(style="Normal")
    r = p.add_run("Langues")
    r.bold = True
    r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)

    if 'langues' in src:
        p = doc.add_paragraph(style="puce_1")
        r = p.add_run(f"❖ ")
        r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
        langues = []
        for langue in src['langues']:
            l, niveau = langue['langue'], langue['niveau']
            langues.append(f'{l} ({niveau})')
        p.add_run(", ".join(langues))

    doc.add_paragraph(" ")

    doc.add_paragraph("FORMATION", style="section")
    if "diplomes" in src:
        for diplome in src["diplomes"]:
            annee, intitule, etablissement = diplome['date_obtention'], diplome['intitule'], diplome['etablissement']
            p = doc.add_paragraph(style="puce_1")  
            r = p.add_run(f"❖ ")
            r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
            if annee:
                r = p.add_run(f"{annee} - ")
                r.bold = True
            r = p.add_run(f"{intitule}")
            r.bold = True
            if etablissement:
                r = p.add_run(f" - {etablissement}")
                r.bold = True
        
    if "certifications" in src:
        for certification in src["certifications"]:
            annee, intitule, etablissement = certification['date_obtention'], certification['intitule'], certification['etablissement']
            p = doc.add_paragraph(style="puce_1")  
            r = p.add_run(f"❖ ")
            r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
            if annee:
                r = p.add_run(f"{annee} - ")
            r = p.add_run(f"{intitule}")
            if etablissement:
                r = p.add_run(f" - {etablissement}")
    if "formations" in src and src["formations"] != []:
        for formation in src["formations"]:
            annee, intitule, etablissement = formation['date_obtention'], formation['intitule'], formation['etablissement']
            p = doc.add_paragraph(style="puce_1")  
            r = p.add_run(f"❖ ")
            r.font.color.rgb = RGBColor(0x2F, 0x55, 0x97)
            if annee:
                r = p.add_run(f"{annee} - ")
            r = p.add_run(f"{intitule}")
            if etablissement:
                r = p.add_run(f" - {etablissement}")


    if output_path is None:
        output_path = os.path.splitext(input_file_path)[0] + "_output.docx" if input_file_path else os.path.splitext(source_json)[0] + "_output.docx"

    if os.path.exists(output_path):
        os.remove(output_path)
    doc.save(output_path)
    print(f'saved {output_path}')

    return output_path

def generate_word(source_json, target_template, output_path, input_file_path=None):
    """Generate a Word document from a JSON source and a template.
    This function takes a JSON object as input and generates a Word document
    based on a specified template. The JSON object should contain the data
    to be inserted into the Word document, and the template should be a path
    to a Word document (.docx) that acts as a base for the generated document.

    Args:
        source_json (str): Path to the source JSON file
        target_template (str): Path to the Word template file
        output_path (str): Path where the generated Word file should be saved
        input_file_path (str, optional): Additional input file path
    """
    """Generate a Word document from a JSON source and a template.
    This function takes a JSON object as input and generates a Word document
    based on a specified template. The JSON object should contain the data
    to be inserted into the Word document, and the template should be a path
    to a Word document (.docx) that acts as a base for the generated document.

    Args:
        source_json (_type_): _description_
        target_template (_type_): _description_
    """
    
    doc = None
    if target_template:  # If template is provided, use it
        doc = Document(target_template)
    else:  # Otherwise create a new document
        doc = Document()

    with open(source_json, 'r', encoding='utf-8') as file:
        src = json.load(file)
    
    temp = get_data("denomination_du_poste_recherche", src)
    if temp == "": temp = get_data("dénomination du poste recherché", src)
    
    if temp != "":
        export_trimed_data(temp, "POSTE_RECHERCHE", doc)
        export_data(" ", "POSTE_RECHERCHE", doc)
    else : 
        export_data(" ", "POSTE_RECHERCHE", doc)
        
    separation("DOMAINE D'INTERVENTION", doc)
    
    temp = get_data("resume_du_parcours_professionnel_en_5_lignes", src)
    if temp != "":
        export_trimed_data(temp, "PARCOURS", doc)
    else : 
        export_data(" ", "PARCOURS", doc)
    
    separation("CONNAISSANCES FONCTIONNELLES", doc)
    
    temp = get_data("competences fonctionnelles", src)    
    if temp != "":
        for sub in temp.split('#'):
            export_trimed_data(sub, "LISTE_TACHES", doc, )
    else : 
        export_data(" ", "Normal", doc)
    
    export_data(" ", "Normal", doc)
    separation("CONNAISSANCES TECHNIQUES", doc)
    
    # temp = get_data("langages informatiques", src)
    # if temp != "":
    #     export_data(f'Langages: {temp}', "LISTE_TACHES", doc)
    # else : 
    #     ...
    
    # temp = get_data("technologies_base_de_données", src)
    # if temp != "":
    #     export_data(f'Base de données: {temp}', "LISTE_TACHES", doc)
    # else : 
    #     ...
    
    # temp = get_data("systèmes_d_exploitation", src)
    # if temp != "":
    #     export_data(f'Systèmes: {temp}', "LISTE_TACHES", doc)
    # else : 
    #     ...
    
    # temp = get_data("outils_informatiques", src)
    # if temp != "":
    #     export_data(f'Outils: {temp}', "LISTE_TACHES", doc)
    # else : 
    #     ...
    
    # temp = get_data("méthodologies", src)
    # if temp != "":
    #     export_data(f'Méthodologies: {temp}', "LISTE_TACHES", doc)
    # else : 
    #     ...
    
    # temp = get_data("autres_compétences_techniques", src)
    # if temp != "":
    #     export_data(f'Connaissances diverses: {temp}', "CONNAISSANCES_DIVERSES", doc)
    # else : 
    #     ...

    temp = get_data("competences techniques", src)
    if temp != "":
        for part in temp.split('#'):
            export_trimed_data(part, "LISTE_TACHES", doc)
        export_data(" ", "Normal", doc)
    else:
        ...

    
    export_data(" ", "Normal", doc)
    
    separation("DIPLOMES", doc)
    
    if "diplomes" in src:
        for diplome in src["diplomes"]:
            annee, intitule, etablissement = diplome['date_obtention'], diplome['intitule'], diplome['etablissement']
            export_trimed_data(f'{annee}: {intitule} - {etablissement}', "LISTE_TACHES", doc)
        export_data(" ", "Normal", doc)
    else:
        export_data(" ", "Normal", doc)
        
    if "certifications" in src:
        separation("CERTIFICATIONS", doc)
        for certification in src["certifications"]:
            annee, intitule, etablissement = certification['date_obtention'], certification['intitule'], certification['etablissement']
            export_trimed_data(f'{annee}: {intitule} - {etablissement}', "LISTE_TACHES", doc)
        export_data(" ", "Normal", doc)
    else:
        if "formations" in src and src["formations"] != []:
            separation("CERTIFICATIONS", doc)
            for formation in src["formations"]:
                annee, intitule, etablissement = formation['date_obtention'], formation['intitule'], formation['etablissement']
                export_trimed_data(f'{annee}: {intitule} - {etablissement}', "LISTE_TACHES", doc)
            export_data(" ", "Normal", doc)
        else:
            export_data(" ", "Normal", doc)
    
    separation("LANGUES", doc)
    
    if 'langues' in src:
        for langue in src['langues']:
            l, niveau = langue['langue'], langue['niveau']
            export_trimed_data(f'{l}: {niveau}', "LANGUE", doc)
        export_data(" ", "Normal", doc)
    else:
        export_data(" ", "Normal", doc)
    
    separation("EXPERIENCES PROFESSIONNELLES", doc)
    export_data(" ", "Normal", doc)
    
    for xp in src['experience']:
        entreprise, debut, fin = xp['entreprise'], xp['date_debut'], xp['date_fin']
        export_trimed_data(f'{entreprise} ({debut} - {fin})', "ENTREPRISE_DATE", doc)
        export_data(" ", "Normal", doc)
        
        poste = xp['poste_occupe']
        export_trimed_data(poste, "POSTE_OCCUPE", doc)
        export_data(" ", "Normal", doc)
        
        if xp['contexte de la mission']:
            export_data("Contexte", "CONTEXTE_PROJET", doc)
            
            ctxt = xp['contexte de la mission']
            for part in ctxt.split('#'):
                export_trimed_data(part, "LISTE_PROJET", doc)
            export_data(" ", "Normal", doc)
        
        export_data("Activités:", "DETAILS_TACHES", doc)
        
        taches = xp['taches']
        for t in taches.split('#'):
            if t.startswith('**'): 
                export_trimed_data(t.replace('**', ''), "TITRE_LISTE_TACHES", doc)
                export_data(" ", "Normal", doc)
            else: export_data(t, "LISTE_TACHES", doc)
        export_data(" ", "Normal", doc)
        
        env = xp['environnement_technique']
        if env:
            export_trimed_data(f'Environnement technique: {env}', "ENVIRONNEMENT_TECHNIQUE", doc)
            export_data(" ", "Normal", doc)
        export_data(" ", "Normal", doc)
    
    # récupérer le nom du json sans l'extension
    # nom_fichier = source_json.split('.')[0]
    # output_path = f'{nom_fichier}.docx'
    if output_path is None:
        output_path = os.path.splitext(input_file_path)[0] + "_output.docx" if input_file_path else os.path.splitext(source_json)[0] + "_output.docx"

    if os.path.exists(output_path):
        os.remove(output_path)
    doc.save(output_path)
    print(f'saved {output_path}')

    return output_path

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a Word document from a JSON source and a template.")
    parser.add_argument('--json', type=str, help='The path to the JSON file containing the data.')
    parser.add_argument('--template', type=str, help='The path to the Word template file.')
    parser.add_argument('--content', type=str, help='The content to be inserted into a Word document.')
    parser.add_argument('--output', type=str, help='The path to save the generated Word document.')
    parser.add_argument('--test', type=str, help='For test purpose')
    args = parser.parse_args()

    if args.test:
        print("Test mode activated.")
        
        quit()

    if args.json and args.template and args.output:
        generate_word_new(args.json, args.template, args.output)
    elif args.content:
        generate_word_new(None, None, args.content)
    else:
        print("Please provide either a JSON file or content to insert.")
