import streamlit as st
from utils.pdf_extractor import PDFTextExtractor
from utils.skills_extractor import SkillsExtractor
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.recommendations import RecommendationGenerator
import os
# Initialize components
os.system('python -m spacy download en_core_web_sm')

pdf_extractor = PDFTextExtractor()
skills_extractor = SkillsExtractor("models/skills_data.json")
sentiment_analyzer = SentimentAnalyzer()
recommendation_generator = RecommendationGenerator("models/skills_data.json")

# Streamlit app
st.title("Resume Analyzer Pro")

# Sidebar: Specify a category
st.sidebar.header("Category Match Analysis")
selected_category = st.sidebar.selectbox(
    "Select a Category", list(skills_extractor.skills_data["categories"].keys())
)

# File uploader
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
if uploaded_file:
    # Extract text from the uploaded PDF
    resume_text = pdf_extractor.extract_text_from_pdf(uploaded_file)
    
    # Split the resume into sections
    sections = pdf_extractor.split_resume_into_sections(resume_text)
    
    # Extract skills using keyword matching
    skills = skills_extractor.extract_skills_keywords(resume_text)
    
    # Calculate category scores
    category_scores = skills_extractor.calculate_category_scores(skills)
    max_possible_score = max(category_scores.values()) if category_scores else 1
    category_percentages = {
        cat: (score / max_possible_score) * 100 for cat, score in category_scores.items()
    }
    most_relevant_category = max(category_scores, key=category_scores.get)
    
    # Perform sentiment analysis
    sentiment = sentiment_analyzer.analyze_sentiment(resume_text)
    
    # Generate recommendations
    recommendations = recommendation_generator.generate_recommendations(
        selected_category, skills, sentiment
    )
    
    # Display results
    st.subheader("Analysis Results")
    st.write(f"**Most Relevant Category:** {most_relevant_category}")
    st.write(
        f"**Match Percentage for Selected Category ({selected_category}):** "
        f"{category_percentages[selected_category]:.2f}%"
    )
    
    # Display most relevant skills with numbering and frequencies
    st.subheader("Most Relevant Skills")
    ranked_skills = skills_extractor.rank_skills(skills)
    if ranked_skills:
        for i, (skill, count) in enumerate(ranked_skills[:10], start=1):
            st.success(f"{i}. {skill}: {count}")
    else:
        st.write("No relevant skills found in the resume.")
    
    # Keyword highlighting
    st.subheader("Keyword Highlighting")
    highlighted_text = skills_extractor.highlight_keywords(resume_text, skills)
    st.markdown(highlighted_text, unsafe_allow_html=True)
    
    # Sentiment analysis
    st.subheader("Sentiment Analysis")
    st.write(
        f"Positive: {sentiment['pos']:.2f}, Negative: {sentiment['neg']:.2f}, Neutral: {sentiment['neu']:.2f}"
    )
    
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
user_skills_input = st.text_area(
    "Enter skills separated by commas (e.g., Python, Docker, Kubernetes):"
)
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