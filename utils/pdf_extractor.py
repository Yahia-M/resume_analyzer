import pdfplumber
import re

class PDFTextExtractor:
    def extract_text_from_pdf(self, file):
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages)

    def split_resume_into_sections(self, text):
        patterns = {
            "experience": r"(?i)(experience|work history|professional experience)",
            "projects": r"(?i)(projects|project experience|projets académiques)",
            "competences": r"(?i)(skills|competences|technical skills|key skills|compétences)"
        }
        sections = {"experience": "", "projects": "", "competences": ""}
        current_section = None
        for line in text.split("\n"):
            normalized_line = line.strip().lower()
            for section, pattern in patterns.items():
                if re.search(pattern, normalized_line):
                    current_section = section
                    break
            if current_section:
                sections[current_section] += line + "\n"
        return sections