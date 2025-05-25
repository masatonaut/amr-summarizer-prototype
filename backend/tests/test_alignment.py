from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_process_article():
    response = client.post(
        "/process_article",
        json={
            "summary": "Test summary",
            "article": "Sentence one. Sentence two. Sentence three. Sentence four.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    # Check that the response contains expected keys
    assert "top_sentences" in data
    assert "similarity_scores" in data
    # Optionally, verify there are exactly three top sentences
    assert len(data["top_sentences"]) == 3


def test_process_amr():
    response = client.post(
        "/process_amr",
        json={
            "summary": "Test summary",
            "article": "Sentence one. Sentence two. Sentence three. Sentence four.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    # Check that the response contains AMR graph keys
    assert "summary_amr" in data
    assert "top_sentence_amrs" in data
