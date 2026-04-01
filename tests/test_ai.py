import pytest
from unittest.mock import MagicMock, patch
from app.ai import CVAnalysis, JobMatchAnalysis, analyze_cv, match_cv_with_jd

@patch("app.ai.client")
def test_analyze_cv(mock_client):
    # Mock the response from OpenAI/Instructor
    mock_response = CVAnalysis(
        summary="Experienced developer",
        recommendation="Strong fit",
        skills=["Python", "Go", "FastAPI"],
        experience_highlights=["Worked at ADL", "Built microservices"],
        fit_score=95
    )
    mock_client.chat.completions.create.return_value = mock_response

    result = analyze_cv("Sample CV text")
    
    assert result.summary == "Experienced developer"
    assert "Python" in result.skills
    assert result.fit_score == 95

@patch("app.ai.client")
def test_match_cv_with_jd(mock_client):
    # Mock the response from OpenAI/Instructor
    mock_response = JobMatchAnalysis(
        score=85,
        matched_skills=["Python", "FastAPI"],
        missing_skills=["Kubernetes"],
        explanation="Good technical match, missing cloud experience.",
        verdict="Potential Match"
    )
    mock_client.chat.completions.create.return_value = mock_response

    result = match_cv_with_jd("Sample CV", "Sample JD")
    
    assert result.score == 85
    assert "Kubernetes" in result.missing_skills
    assert result.verdict == "Potential Match"
