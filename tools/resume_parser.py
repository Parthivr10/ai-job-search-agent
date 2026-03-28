import pdfplumber


def extract_resume_text(path):

    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"

    return text
