# 💬 resume_analyzer

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
import streamlit as st
import pdfplumber
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import torch
import re
import spacy
from transformers import pipeline
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from fpdf import FPDF  # For generating PDF reports
import os
from datetime import datetime
import json  # Import the JSON module

# Download NLTK data for sentiment analysis
nltk.download("vader_lexicon")

# Check if GPU is available and set the device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load spaCy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Load skills data from JSON file
with open("models/skills_data.json", "r") as file:
    skills_data = json.load(file)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to split resume into sections
def split_resume_into_sections(text):
    patterns = {
        "experience": r"(?i)(experience|work history|professional experience)",
        "projects": r"(?i)(projects|project experience|projets académiques)",
        "competences": r"(?i)(skills|competences|technical skills|key skills|compétences)"
    }
    sections = {"experience": "", "projects": "", "competences": ""}
    lines = text.split("\n")
    current_section = None
    for line in lines:
        normalized_line = line.strip().lower()
        for section, pattern in patterns.items():
            if re.search(pattern, normalized_line):
                current_section = section
                break
        if current_section:
            sections[current_section] += line + "\n"
    return sections

# Function to categorize the resume using the embedded knowledge base
def calculate_category_scores(skills):
    category_scores = {}
    for category, skill_groups in skills_data["categories"].items():
        score = 0
        for skill_group in skill_groups.values():
            score += sum(skill in skills for skill in skill_group)
        category_scores[category] = score
    return category_scores

# Function to extract skills using keyword matching
def extract_skills_keywords(text):
    doc = nlp(text)
    skills_found = []
    for category, skill_groups in skills_data["categories"].items():
        for skill_group in skill_groups.values():
            skills_found.extend([skill for skill in skill_group if skill.lower() in text.lower()])
    return skills_found

# Function to rank skills by relevance
def rank_skills(skills):
    ranked_skills = Counter(skills).most_common()
    return ranked_skills

# Function to perform sentiment analysis
def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    return sentiment

# Streamlit app
st.title("Resume Analyzer Pro")

# Sidebar: Specify a category
st.sidebar.header("Category Match Analysis")
selected_category = st.sidebar.selectbox("Select a Category", list(skills_data["categories"].keys()))

# File uploader
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
if uploaded_file:
    # Extract text from the uploaded PDF
    resume_text = extract_text_from_pdf(uploaded_file)
    
    # Split the resume into sections
    sections = split_resume_into_sections(resume_text)
    
    # Extract skills using keyword matching
    skills = extract_skills_keywords(resume_text)
    
    # Calculate category scores
    category_scores = calculate_category_scores(skills)
    max_possible_score = max(category_scores.values()) if category_scores else 1
    category_percentages = {cat: (score / max_possible_score) * 100 for cat, score in category_scores.items()}
    most_relevant_category = max(category_scores, key=category_scores.get)
    
    # Perform sentiment analysis
    sentiment = analyze_sentiment(resume_text)
    
    # Generate recommendations
    recommendations = []
    if selected_category in skills_data["categories"]:
        required_skills = set(skill for group in skills_data["categories"][selected_category].values() for skill in group)
        missing_skills = required_skills - set(skills)
        if missing_skills:
            recommendations.append(f"Consider adding these missing skills: {', '.join(missing_skills)}")
    if sentiment["neg"] > 0.2:
        recommendations.append("Your resume contains negative language. Consider revising it for a more positive tone.")
    
    # Display results
    st.subheader("Analysis Results")
    st.write(f"**Most Relevant Category:** {most_relevant_category}")
    st.write(f"**Match Percentage for Selected Category ({selected_category}):** {category_percentages[selected_category]:.2f}%")
    
    # Display most relevant skills with numbering and frequencies
    st.subheader("Most Relevant Skills")
    ranked_skills = rank_skills(skills)
    if ranked_skills:
        for i, (skill, count) in enumerate(ranked_skills[:10], start=1):
            st.success(f"{i}. {skill}: {count}")
    else:
        st.write("No relevant skills found in the resume.")
    
    # Keyword highlighting
    st.subheader("Keyword Highlighting")
    highlighted_text = resume_text
    for skill in skills:
        highlighted_text = re.sub(
            rf"\b{re.escape(skill)}\b",
            f"<span style='background-color: #D4F5D4; padding: 2px 5px; border-radius: 4px;'>{skill}</span>",
            highlighted_text,
            flags=re.IGNORECASE
        )
    st.markdown(highlighted_text, unsafe_allow_html=True)
    
    # Sentiment analysis
    st.subheader("Sentiment Analysis")
    st.write(f"Positive: {sentiment['pos']:.2f}, Negative: {sentiment['neg']:.2f}, Neutral: {sentiment['neu']:.2f}")
    
    # Recommendations
    st.subheader("Recommendations")
    if recommendations:
        for rec in recommendations:
            st.warning(rec)
    else:
        st.success("Your resume looks great! No major improvements needed.")

# Manual Skill Search Section
st.header("Manually Input Skills")
st.write("Enter skills below to check if they are mentioned in the resume.")
user_skills_input = st.text_area("Enter skills separated by commas (e.g., Python, Docker, Kubernetes):")
if user_skills_input:
    user_skills = [skill.strip() for skill in user_skills_input.split(",")]
    st.subheader("Skills Presence in Resume")
    if uploaded_file:
        for skill in user_skills:
            if skill.lower() in resume_text.lower():
                st.success(f"✅ {skill} found in the resume.")
            else:
                st.error(f"❌ {skill} not found in the resume.")
    else:
        st.warning("Please upload a resume first to check for skills presence.")