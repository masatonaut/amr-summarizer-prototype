import pytest
from fastapi.testclient import TestClient
from amrsummarizer.main import app

# Create a TestClient instance for our FastAPI app
client = TestClient(app)


def test_process_article_ok():
    """
    Integration test: /process_article should return 200 OK
    for a valid payload and include both expected keys.
    """
    res = client.post(
        "/process_article",
        json={"summary": "Test", "article": "One sentence. Another sentence."},
    )
    assert res.status_code == 200
    body = res.json()
    # Verify that the response contains the top_sentences list and similarity_scores list
    assert "top_sentences" in body and "similarity_scores" in body


@pytest.mark.parametrize(
    "payload,code",
    [
        # Missing both summary and article should trigger 400 Bad Request
        ({"summary": "", "article": ""}, 400),
        # Special "simulate error" payload should trigger 500 Internal Server Error
        ({"summary": "simulate error", "article": "simulate error"}, 500),
    ],
)
def test_process_article_error(payload, code):
    """
    Parameterized integration tests for /process_article error handling.
    Ensures correct HTTP status codes for invalid payloads.
    """
    res = client.post("/process_article", json=payload)
    assert res.status_code == code


def test_process_amr_ok():
    """
    Integration test: /process_amr should return 200 OK
    and include an SVG string plus a dict of top_sentence_svgs.
    """
    res = client.post(
        "/process_amr", json={"summary": "S", "article": "One. Two. Three. Four."}
    )
    assert res.status_code == 200
    data = res.json()
    # The summary_svg should contain SVG content
    assert "<svg" in data["summary_svg"]
    # top_sentence_svgs should be a dictionary mapping sentences to SVG strings
    assert isinstance(data["top_sentence_svgs"], dict)
