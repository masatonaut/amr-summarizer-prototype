import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_process_article_ok():
    res = client.post("/process_article", json={
      "summary":"Test","article":"One sentence. Another sentence."
    })
    assert res.status_code == 200
    body = res.json()
    assert "top_sentences" in body and "similarity_scores" in body

@pytest.mark.parametrize("payload,code", [
  ({"summary":"","article":""}, 400),
  ({"summary":"simulate error","article":"simulate error"}, 500),
])
def test_process_article_error(payload, code):
    assert client.post("/process_article", json=payload).status_code == code

def test_process_amr_ok():
    res = client.post("/process_amr", json={
      "summary":"S","article":"One. Two. Three. Four."
    })
    assert res.status_code == 200
    data = res.json()
    assert "<svg" in data["summary_svg"]
    assert isinstance(data["top_sentence_svgs"], dict)
