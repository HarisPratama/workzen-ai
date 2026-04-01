import os
from typing import List
from openai import OpenAI
from pydantic import BaseModel, Field
import instructor
from dotenv import load_dotenv

load_dotenv()

# Define the schema for structured output
class CVAnalysis(BaseModel):
    summary: str = Field(..., description="High-level summary of the candidate's profile")
    recommendation: str = Field(..., description="Fit or Not Fit recommendation with brief reasoning")
    skills: List[str] = Field(..., description="List of technical and soft skills extracted from the CV")
    experience_highlights: List[str] = Field(..., description="Key professional roles or achievements")
    fit_score: int = Field(..., ge=0, le=100, description="Overall fit score from 0 to 100")

class JobMatchAnalysis(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Overall match score between CV and JD")
    matched_skills: List[str] = Field(..., description="Skills found in both the CV and the JD")
    missing_skills: List[str] = Field(..., description="Required JD skills that are missing in the CV")
    explanation: str = Field(..., description="Detailed reasoning for the match score")
    verdict: str = Field(..., description="Final verdict: 'Strong Match', 'Potential Match', or 'Not a Match'")

# Initialize the model with Instructor and OpenRouter
# Gunakan mode JSON_SCHEMA agar lebih kompatibel dengan berbagai model di OpenRouter
client = instructor.patch(
    OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    ),
    mode=instructor.Mode.JSON
)

def analyze_cv(cv_text: str) -> CVAnalysis:
    """
    Analyzes CV text using OpenRouter and returns a structured JSON object.
    """
    return client.chat.completions.create(
        model="qwen/qwen3.6-plus-preview:free",
        response_model=CVAnalysis,
        messages=[
            {
                "role": "system",
                "content": "You are an HR expert at a top tech company. Analyze the provided CV carefully."
            },
            {
                "role": "user",
                "content": f"Analyze this CV text and provide a structured JSON response:\n\n{cv_text}"
            }
        ]
    )

def match_cv_with_jd(cv_text: str, jd_text: str) -> JobMatchAnalysis:
    """
    Matches a CV against a Job Description and returns a structured gap analysis.
    """
    return client.chat.completions.create(
        model="qwen/qwen3.6-plus-preview:free",
        response_model=JobMatchAnalysis,
        messages=[
            {
                "role": "system",
                "content": "You are an expert technical recruiter. Compare the candidate's CV against the Job Description to identify matches and gaps."
            },
            {
                "role": "user",
                "content": f"Analyze the match between this CV and Job Description:\n\nCV:\n{cv_text}\n\nJob Description:\n{jd_text}"
            }
        ]
    )
