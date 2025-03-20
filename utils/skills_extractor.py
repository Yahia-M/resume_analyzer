import re
from collections import Counter
import spacy
import json

class SkillsExtractor:
    def __init__(self, skills_data_path):
        self.skills_data = self.load_skills_data(skills_data_path)
        self.nlp = spacy.load("en_core_web_sm")

    @staticmethod
    def load_skills_data(path):
        with open(path, "r") as file:
            return json.load(file)

    def calculate_category_scores(self, skills):
        category_scores = {}
        for category, skill_groups in self.skills_data["categories"].items():
            score = sum(skill in skills for group in skill_groups.values() for skill in group)
            category_scores[category] = score
        return category_scores

    def extract_skills_keywords(self, text):
        doc = self.nlp(text)
        skills_found = []
        for category, skill_groups in self.skills_data["categories"].items():
            for skill_group in skill_groups.values():
                skills_found.extend([skill for skill in skill_group if skill.lower() in text.lower()])
        return skills_found

    def rank_skills(self, skills):
        return Counter(skills).most_common()

    def highlight_keywords(self, text, skills):
        highlighted_text = text
        for skill in skills:
            highlighted_text = re.sub(
                rf"\b{re.escape(skill)}\b",
                f"<span style='background-color: #D4F5D4; padding: 2px 5px; border-radius: 4px;'>{skill}</span>",
                highlighted_text,
                flags=re.IGNORECASE
            )
        return highlighted_text