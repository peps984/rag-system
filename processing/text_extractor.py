from pathlib import Path
from processing.extractors import pdf_extractor, docx_extractor, text_extractor


def text_extractor(file_path):
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == '.pdf':
        text = pdf_extractor(file_path)
    elif suffix == '.docx':
        text = docx_extractor(file_path)
    elif suffix in ['.txt', '.md']:
        text = text_extractor(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    return(text)