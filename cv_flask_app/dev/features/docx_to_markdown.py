import os
from docx import Document
import markdownify

def convert_docx_to_markdown(docx_path, output_md_path):
    """
    Extracts text from a DOCX file and converts it to Markdown format.

    Args:
        docx_path (str): Path to the input DOCX file.
        output_md_path (str): Path to save the output Markdown file.

    Returns:
        str: The extracted and converted Markdown text, or None if an error occurs.
    """
    try:
        doc = Document(docx_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        
        # Basic conversion to Markdown. For more complex DOCX features (tables, images),
        # a more sophisticated library or custom logic would be needed.
        markdown_content = "\n".join(full_text)
        
        # Use markdownify for better conversion if available and needed
        # from docx2python import docx2python
        # with docx2python(docx_path) as docx_content:
        #     markdown_content = docx_content.text_md

        with open(output_md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return markdown_content
    except Exception as e:
        print(f"Error converting DOCX to Markdown: {e}")
        return None

if __name__ == "__main__":
    # Example usage:
    # Create a dummy DOCX file for testing
    # from docx import Document
    # doc = Document()
    # doc.add_heading('Test Document', level=1)
    # doc.add_paragraph('This is a paragraph in the test document.')
    # doc.add_paragraph('Another paragraph with some bold text.', style='Intense Quote')
    # doc.save('test_input.docx')

    # input_docx = 'test_input.docx'
    # output_md = 'test_output.md'
    # converted_text = convert_docx_to_markdown(input_docx, output_md)
    # if converted_text:
    #     print(f"Successfully converted '{input_docx}' to '{output_md}'")
    #     print("\n--- Converted Content ---")
    #     print(converted_text)
    # else:
    #     print(f"Failed to convert '{input_docx}'")
    pass