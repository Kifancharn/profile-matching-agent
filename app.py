import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
import os

# ==========================
# Load Gemini API Key
# ==========================
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================
# PDF Reader
# ==========================
def extract_pdf_text(uploaded_file):

    pdf_reader = PdfReader(uploaded_file)

    text = ""

    for page in pdf_reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ==========================
# DOCX Reader
# ==========================
def extract_docx_text(uploaded_file):

    doc = Document(uploaded_file)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


# ==========================
# Generic File Reader
# ==========================
def get_file_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_pdf_text(uploaded_file)

    elif file_name.endswith(".docx"):
        return extract_docx_text(uploaded_file)

    elif file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    return ""


# ==========================
# Streamlit UI
# ==========================
st.set_page_config(
    page_title="GSK Profile Matching Agent",
    layout="wide"
)

st.title("🔍 GSK Profile Matching Agent")

st.markdown("### Upload Job Description and Resume")

# JD Upload
jd_file = st.file_uploader(
    "Upload Job Description",
    type=["pdf", "docx", "txt"]
)

# Resume Upload
resume_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx", "txt"]
)

# ==========================
# Analyze Button
# ==========================
if st.button("🚀 Analyze Candidate"):

    if jd_file is None:
        st.error("Please upload a Job Description file")
        st.stop()

    if resume_file is None:
        st.error("Please upload a Resume file")
        st.stop()

    with st.spinner("Reading files..."):

        jd_text = get_file_text(jd_file)

        resume_text = get_file_text(resume_file)

    with st.spinner("Analyzing candidate profile..."):

        prompt = f"""
You are a Senior Cyber Security Recruitment Analyst at GSK.

Analyze the candidate profile against the Job Description.

Return the response in this exact format.

# Overall Match Score
Score from 1 to 5

# Match Percentage
0 to 100%

# Executive Summary

# Matching Skills

# Missing Skills

# Emerging Security Skills

Mention security skills that are not explicitly required
but could benefit GSK.

Examples:
- AI Security
- GenAI Security
- Zero Trust
- CNAPP
- DSPM
- Container Security
- Kubernetes Security
- Cloud Native Security
- Security Automation

# Recommendation

Strongly Recommended
Recommended
Not Recommended

# Why GSK Should Consider This Candidate

------------------------------------------------

JOB DESCRIPTION

{jd_text}

------------------------------------------------

RESUME

{resume_text}
"""

        try:

            response = model.generate_content(prompt)

            st.success("Analysis Complete")

            st.markdown(response.text)

        except Exception as e:

            st.error(f"Error: {str(e)}")