import json

class RecommendationGenerator:
    def __init__(self, skills_data_path):
        self.skills_data = self.load_skills_data(skills_data_path)

    @staticmethod
    def load_skills_data(path):
        with open(path, "r") as file:
            return json.load(file)

    def generate_recommendations(self, selected_category, skills, sentiment):
        recommendations = []
        if selected_category in self.skills_data["categories"]:
            required_skills = set(skill for group in self.skills_data["categories"][selected_category].values() for skill in group)
            missing_skills = required_skills - set(skills)
            if missing_skills:
                recommendations.append(f"Consider adding these missing skills: {', '.join(missing_skills)}")
        if sentiment["neg"] > 0.2:
            recommendations.append("Your resume contains negative language. Consider revising it for a more positive tone.")
        return recommendations