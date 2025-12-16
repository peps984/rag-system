from pathlib import Path
from pypdf import PdfReader
from docx import Document

def pdf_extractor(file_path):
    
    """
    Extract content from a pdf file
    """
    
    try:
        source = Path(file_path)
        reader = PdfReader(source)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
        return(text.strip())
    
    except Exception as e:
        raise Exception(f"Error extracting pdf: {str(e)}")

def docx_extractor(file_path):
    
    """
    Extract content from a docx file
    """
    
    try:
        source = str(file_path)
        doc = Document(source)
        
        text = ""
        for par in doc.paragraphs:
            text += par.text + "\n"
        
        return(text.strip())
    
    except Exception as e:
        raise Exception(f"Error extracting docx: {str(e)}")

def text_extractor(file_path):
    
    """
    Extract content from a txt or md file
    """
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return(text.strip())
    
    except Exception as e:
        raise Exception(f"Error extracting txt/md: {str(e)}")